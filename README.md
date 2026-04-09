# env-vault

> CLI tool for encrypting and versioning environment variables across projects

---

## Installation

```bash
pip install env-vault
```

Or with [pipx](https://pypa.github.io/pipx/) (recommended for CLI tools):

```bash
pipx install env-vault
```

---

## Usage

Initialize a vault in your project directory:

```bash
env-vault init
```

Add and encrypt an environment variable:

```bash
env-vault set DATABASE_URL "postgres://user:pass@localhost/mydb"
```

Retrieve a decrypted value:

```bash
env-vault get DATABASE_URL
```

Export all variables to a `.env` file:

```bash
env-vault export > .env
```

Push a versioned snapshot to share across your team:

```bash
env-vault push --tag v1.2.0
```

---

## How It Works

`env-vault` encrypts your environment variables using AES-256 and stores versioned snapshots locally or in a remote backend (S3, Git). Each project maintains its own isolated vault, keeping secrets out of your source code and shell history.

---

## License

This project is licensed under the [MIT License](LICENSE).