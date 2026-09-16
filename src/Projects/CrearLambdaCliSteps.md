# Crear una AWS Lambda amb AWS CLI i integrar-la amb S3

Aquesta guia descriu com crear, configurar, desplegar i provar una funció AWS Lambda utilitzant AWS CLI.

L'objectiu final serà implementar aquest flux:

```text
            Upload
              │
              ▼
┌───────────────────────────┐
│ S3: input-for-a-lambda    │
└─────────────┬─────────────┘
              │
              │ S3 ObjectCreated
              ▼
┌───────────────────────────┐
│ Lambda: my-lambda         │
│                           │
│ 1. Llegeix l'objecte      │
│ 2. Processa l'objecte     │
│ 3. El copia al destí      │
└─────────────┬─────────────┘
              │
              │ PutObject
              ▼
┌───────────────────────────┐
│ S3: output-for-a-lambda   │
└───────────────────────────┘
```

---

# 1. Crear la funció Lambda

Crea el fitxer:

```text
lambda_function.py
```

Per exemple:

```python
def lambda_handler(event, context):
    print("Lambda executada correctament")

    return {
        "statusCode": 200,
        "body": "Hello from Lambda!"
    }
```

L'handler serà:

```text
lambda_function.lambda_handler
```

---

# 2. Crear el paquet ZIP

Empaqueta el codi:

```bash
zip function.zip lambda_function.py
```

Obtindrem:

```text
lambda_function.py
        │
        │ zip
        ▼
   function.zip
```

---

# 3. Crear la Trust Policy d'IAM

La Lambda necessita un IAM Role que pugui assumir durant l'execució.

Crea:

```text
trust-policy.json
```

amb:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

Aquesta política permet que AWS Lambda assumeixi el role.

---

# 4. Afegir permisos a l'usuari IAM

L'usuari que utilitza AWS CLI necessita permisos per crear i administrar la Lambda i el seu IAM Role.

Per exemple:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ManageLambda",
      "Effect": "Allow",
      "Action": [
        "lambda:CreateFunction",
        "lambda:UpdateFunctionCode",
        "lambda:UpdateFunctionConfiguration",
        "lambda:GetFunction",
        "lambda:InvokeFunction",
        "lambda:DeleteFunction"
      ],
      "Resource": "*"
    },
    {
      "Sid": "ManageLambdaRole",
      "Effect": "Allow",
      "Action": [
        "iam:CreateRole",
        "iam:GetRole",
        "iam:AttachRolePolicy",
        "iam:DetachRolePolicy",
        "iam:PassRole"
      ],
      "Resource": "arn:aws:iam::321572485002:role/my-lambda-role"
    }
  ]
}
```

> `iam:PassRole` és necessari perquè l'usuari pugui assignar `my-lambda-role` a la funció Lambda.

---

# 5. Crear l'IAM Role de la Lambda

Crea el role:

```bash
aws iam create-role \
  --role-name my-lambda-role \
  --assume-role-policy-document file://trust-policy.json
```

Associa la política bàsica de Lambda:

```bash
aws iam attach-role-policy \
  --role-name my-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

Aquesta política permet que la Lambda escrigui logs a CloudWatch.

Comprova les polítiques:

```bash
aws iam list-attached-role-policies \
  --role-name my-lambda-role
```

---

# 6. Obtenir l'ARN del role

```bash
ROLE_ARN=$(aws iam get-role \
  --role-name my-lambda-role \
  --query 'Role.Arn' \
  --output text)
```

Comprova'l:

```bash
echo "$ROLE_ARN"
```

Per exemple:

```text
arn:aws:iam::321572485002:role/my-lambda-role
```

---

# 7. Crear la funció Lambda

```bash
aws lambda create-function \
  --function-name my-lambda \
  --runtime python3.13 \
  --role "$ROLE_ARN" \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://function.zip \
  --region eu-central-1
```

La regió:

```text
eu-central-1
```

correspon a **Europe (Frankfurt)**.

---

# 8. Provar la Lambda manualment

```bash
aws lambda invoke \
  --function-name my-lambda \
  --payload '{}' \
  --region eu-central-1 \
  response.json
```

Consulta la resposta:

```bash
cat response.json
```

---

# 9. Crear els buckets S3

Utilitzarem dos buckets.

Bucket d'entrada:

```text
input-for-a-lambda
```

Bucket de sortida:

```text
output-for-a-lambda
```

El flux serà:

```text
input-for-a-lambda
        │
        │ GetObject
        ▼
    my-lambda
        │
        │ PutObject
        ▼
output-for-a-lambda
```

---

# 10. Donar permisos S3 a la Lambda

La Lambda necessita:

* `s3:GetObject` per llegir fitxers del bucket d'entrada.
* `s3:PutObject` per escriure fitxers al bucket de sortida.

Aquests permisos s'han d'afegir al role:

```text
my-lambda-role
```

No a l'usuari que executa AWS CLI.

A AWS Console:

```text
IAM
→ Roles
→ my-lambda-role
→ Permissions
→ Add permissions
→ Create inline policy
→ JSON
```

Afegeix:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadInputImages",
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::input-for-a-lambda/*"
    },
    {
      "Sid": "WriteOutputImages",
      "Effect": "Allow",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::output-for-a-lambda/*"
    }
  ]
}
```

Podem anomenar aquesta política:

```text
LambdaS3Access
```

El role quedarà conceptualment així:

```text
my-lambda-role
│
├── AWSLambdaBasicExecutionRole
│     └── CloudWatch Logs
│
├── s3:GetObject
│     └── input-for-a-lambda/*
│
└── s3:PutObject
      └── output-for-a-lambda/*
```

---

# 11. Modificar la Lambda per copiar fitxers entre buckets

Modifica `lambda_function.py`:

```python
import boto3
from urllib.parse import unquote_plus

s3 = boto3.client("s3")

DEST_BUCKET = "output-for-a-lambda"


def lambda_handler(event, context):

    # Obtenir el bucket i el nom del fitxer
    # a partir de l'esdeveniment d'S3.
    bucket = event["Records"][0]["s3"]["bucket"]["name"]

    key = unquote_plus(
        event["Records"][0]["s3"]["object"]["key"]
    )

    print(f"Bucket d'entrada: {bucket}")
    print(f"Fitxer: {key}")

    # Descarregar l'objecte del bucket d'entrada.
    response = s3.get_object(
        Bucket=bucket,
        Key=key
    )

    # Llegir el contingut.
    image_bytes = response["Body"].read()

    print(f"Mida de la imatge: {len(image_bytes)} bytes")

    # Pujar l'objecte al bucket de sortida.
    s3.put_object(
        Bucket=DEST_BUCKET,
        Key=key,
        Body=image_bytes
    )

    print(f"Copiat a: s3://{DEST_BUCKET}/{key}")

    return {
        "statusCode": 200,
        "body": "Imatge copiada correctament"
    }
```

És important llegir:

```python
response["Body"].read()
```

una sola vegada, ja que `Body` és un stream.

---

# 12. Actualitzar el codi de la Lambda

Torna a crear el ZIP:

```bash
zip -j function.zip lambda_function.py
```

Actualitza la Lambda:

```bash
aws lambda update-function-code \
  --function-name my-lambda \
  --zip-file fileb://function.zip \
  --region eu-central-1
```

Espera fins que l'actualització finalitzi:

```bash
aws lambda wait function-updated \
  --function-name my-lambda \
  --region eu-central-1
```

---

# 13. Configurar el trigger d'S3

Ara volem que la Lambda s'executi automàticament quan es pugi un fitxer a:

```text
input-for-a-lambda
```

El trigger serà:

```text
S3 ObjectCreated
```

A AWS Console:

```text
Lambda
→ my-lambda
→ Add trigger
→ S3
```

Configura:

```text
Bucket:
input-for-a-lambda

Event type:
All object create events
```

Confirma la configuració.

A partir d'aquest moment:

```text
Upload a S3
    │
    ▼
ObjectCreated
    │
    ▼
my-lambda
```

---

# 14. Permetre que S3 invoqui la Lambda

El trigger necessita que AWS Lambda permeti al servei S3 executar la funció.

Això és diferent dels permisos `GetObject` i `PutObject`.

Conceptualment:

```text
S3
 │
 │ lambda:InvokeFunction
 ▼
Lambda
```

Mentre que:

```text
Lambda
 │
 ├── s3:GetObject
 │
 └── s3:PutObject
 ▼
S3
```

Quan el trigger es crea des de la consola de Lambda, AWS normalment configura el permís d'invocació necessari.

---

# 15. Donar permís a l'usuari per pujar fitxers

Si volem provar el sistema des del nostre ordinador amb:

```bash
aws s3 cp image.png s3://input-for-a-lambda/
```

l'usuari IAM que executa AWS CLI també necessita:

```text
s3:PutObject
```

Aquest permís és per a **l'usuari**, no per a `my-lambda-role`.

Per exemple:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "UploadInputImages",
      "Effect": "Allow",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::input-for-a-lambda/*"
    }
  ]
}
```

Per tant, tenim dues identitats diferents:

```text
Usuari IAM
│
└── s3:PutObject
      │
      ▼
input-for-a-lambda


my-lambda-role
│
├── s3:GetObject
│      │
│      ▼
│   input-for-a-lambda
│
└── s3:PutObject
       │
       ▼
   output-for-a-lambda
```

---

# 16. Provar el flux complet

Ara podem pujar una imatge:

```bash
aws s3 cp image.png \
  s3://input-for-a-lambda/image.png \
  --region eu-central-1
```

Aquest `PutObject` genera un esdeveniment d'S3.

```text
image.png
    │
    │ aws s3 cp
    ▼
input-for-a-lambda/image.png
    │
    │ ObjectCreated
    ▼
my-lambda
    │
    │ GetObject
    │
    │ processament
    │
    │ PutObject
    ▼
output-for-a-lambda/image.png
```

---

# 17. Comprovar el resultat

Podem comprovar el contingut del bucket de sortida:

```bash
aws s3 ls \
  s3://output-for-a-lambda/ \
  --region eu-central-1
```

Hauríem de veure:

```text
image.png
```

També podem descarregar el resultat:

```bash
aws s3 cp \
  s3://output-for-a-lambda/image.png \
  downloaded-image.png \
  --region eu-central-1
```

---

# 18. Consultar els logs de la Lambda

La Lambda escriu els logs a CloudWatch gràcies a:

```text
AWSLambdaBasicExecutionRole
```

Podem consultar-los des de CLI:

```bash
aws logs tail \
  /aws/lambda/my-lambda \
  --follow \
  --region eu-central-1
```

Quan pugem una imatge hauríem de veure missatges similars a:

```text
Bucket d'entrada: input-for-a-lambda
Fitxer: image.png
Mida de la imatge: 152340 bytes
Copiat a: s3://output-for-a-lambda/image.png
```

---

# 19. Arquitectura final

La configuració completa queda així:

```text
                    IAM User
                       │
                       │ aws s3 cp
                       │ s3:PutObject
                       ▼
          ┌─────────────────────────┐
          │ input-for-a-lambda      │
          │                         │
          │ image.png               │
          └────────────┬────────────┘
                       │
                       │ ObjectCreated
                       ▼
               ┌───────────────┐
               │   my-lambda   │
               └───────┬───────┘
                       │
                 assume role
                       │
                       ▼
               ┌───────────────┐
               │my-lambda-role │
               └───────┬───────┘
                       │
             ┌─────────┴─────────┐
             │                   │
       s3:GetObject        s3:PutObject
             │                   │
             ▼                   ▼
     input-for-a-lambda   output-for-a-lambda
                                 │
                                 │
                                 ▼
                              image.png


               my-lambda
                    │
                    │ logs
                    ▼
             CloudWatch Logs
```

---

# 20. Resum dels permisos

## Usuari IAM

L'usuari que administra i prova la infraestructura necessita, segons les operacions que hagi de realitzar:

```text
lambda:CreateFunction
lambda:UpdateFunctionCode
lambda:UpdateFunctionConfiguration
lambda:GetFunction
lambda:InvokeFunction

iam:CreateRole
iam:GetRole
iam:AttachRolePolicy
iam:PassRole

s3:PutObject
```

## Role de la Lambda

`my-lambda-role` necessita:

```text
AWSLambdaBasicExecutionRole

s3:GetObject
→ arn:aws:s3:::input-for-a-lambda/*

s3:PutObject
→ arn:aws:s3:::output-for-a-lambda/*
```

## Permís d'invocació

S3 necessita permís per executar:

```text
lambda:InvokeFunction
```

sobre:

```text
my-lambda
```

Així obtenim el flux complet:

```text
Upload
  ↓
S3 Input
  ↓
Trigger
  ↓
Lambda
  ↓
GetObject
  ↓
Processament
  ↓
PutObject
  ↓
S3 Output
```

> **Important:** no s'ha de configurar `output-for-a-lambda` com a trigger de la mateixa Lambda. En cas contrari, l'escriptura al bucket de sortida podria tornar a executar la funció i provocar un bucle d'invocacions.
