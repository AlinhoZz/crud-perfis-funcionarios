# CRUD de Perfis de Funcionários (Case Técnico)

API em **Django + Django REST Framework** para gerenciar **perfis de funcionários** com regras de acesso por **departamento**.

---

## ✅ Funcionalidades

- CRUD de **EmployeeProfile** (perfil do funcionário)
- CRUD de **Department** (departamentos)
- Autenticação via **JWT** (SimpleJWT)
- Regras de permissão:
  - **Superuser**: acesso total a todos os perfis
  - **Manager (Gestor)**: pode criar/listar/editar/deletar apenas perfis do **próprio departamento**
  - **Staff (Colaborador)**: não tem acesso ao CRUD (apenas existe como perfil)

---

## 🧠 Regras do Case (implementadas)

### 1) Criar Perfil
Campos obrigatórios no payload:
- `username`, `first_name`, `last_name`, `email`, `password`, `department`

Quem pode criar:
- **Superuser**
- **Manager** do mesmo departamento do perfil criado

### 2) Visualizar/Listar Perfis
- **Super** vê todos
- **Manager** vê apenas do próprio departamento
- Tentativa de acessar perfil de outro departamento → **403**

### 3) Atualizar Perfil
- **Super** pode atualizar qualquer perfil
- **Manager** só atualiza perfis do próprio departamento  
- *(Opcional, se aplicado)* Manager pode ser impedido de alterar `department` e `role`

### 4) Deletar Perfil
- **Super** pode deletar qualquer perfil
- **Manager** só pode deletar perfis do próprio departamento
- Proteção extra: usuário não pode deletar a si mesmo

---

## 🧰 Tecnologias

- Python 3.12+
- Django
- Django REST Framework
- SimpleJWT
- PostgreSQL
- Docker / Docker Compose
- Ruff + Black (lint/format)

---

## 🚀 Como rodar com Docker

### 1) Criar arquivo `.env`
Crie um arquivo em `backend/.env` baseado no exemplo:

```bash
cp backend/.env.example backend/.env
````

### 2) Subir serviços

```bash
docker compose up --build
```

A API ficará disponível em:

* `http://localhost:8000/`

---

## 🔑 Criar superuser e seed inicial

### 1) Criar superuser

```bash
docker compose exec api python manage.py createsuperuser
```

### 2) Criar departamentos

Você pode criar via Django Admin:

* `http://localhost:8000/admin/`

> **Obs.:** Para cadastrar funcionários, é necessário ter departamentos criados previamente.

---

## 🔐 Autenticação (JWT)

### Login

**POST** `/api/token/`

**Body**

```json
{
  "username": "seu_usuario",
  "password": "sua_senha"
}
```

**Resposta**

```json
{
  "refresh": "...",
  "access": "..."
}
```

Use o `access` no header:

```
Authorization: Bearer <TOKEN>
```

### Refresh

**POST** `/api/token/refresh/`

**Body**

```json
{
  "refresh": "..."
}
```

---

## 📌 Endpoints principais

### Employees (Perfis)

Base: `/api/employees/`

* **GET** `/api/employees/` (lista)
* **POST** `/api/employees/` (cria perfil + user)
* **GET** `/api/employees/{id}/` (detalhe)
* **PATCH** `/api/employees/{id}/` (atualiza)
* **DELETE** `/api/employees/{id}/` (deleta)

### Departments

Base: `/api/departments/`

* **GET** `/api/departments/` (lista)
* **POST** `/api/departments/` (cria) *(apenas admin/superuser, se habilitado)*
* **PATCH** `/api/departments/{id}/`
* **DELETE** `/api/departments/{id}/`

---

## 🔍 Busca e filtros

No endpoint de perfis:

* `?search=` busca por:

  * `username`, `first_name`, `last_name`, `email`
* `?department=` filtra por departamento (id)

**Exemplos**

* `/api/employees/?search=pedro`
* `/api/employees/?department=1`
* `/api/employees/?search=pedro&department=1`

---

## 🧪 Qualidade de código (lint/format)

Rodar lint/format dentro do container:

```bash
docker compose exec api ruff check . --fix
docker compose exec api black .
```

---

## 📄 Observações importantes

* Para o sistema funcionar corretamente, é necessário existir pelo menos:

  * um **superuser**
  * **departamentos** cadastrados
* Usuários com perfil **Manager** devem ter `EmployeeProfile` associado para operar o CRUD.

````
 `backend/.env.example`

Crie o arquivo `backend/.env.example` com:

env
DJANGO_SECRET_KEY=dev-secret-key
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=*

DB_NAME=crud_perfis
DB_USER=crud_perfis
DB_PASSWORD=crud_perfis
DB_HOST=db
DB_PORT=5432

