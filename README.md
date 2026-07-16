# spadio

**Django Application Runtime Framework ** is the **core Python/Django package** for Django apps, providing **shared utilities, base classes, and common components** used across all modules of the django ecosystem.

It is designed to **reduce code duplication**, enforce **consistent patterns**, and serve as the foundation for modular educational management apps.

---


## Installation

```bash
pip install spadio
```

---

## Usage

Once installed, you can import and use the shared components in any module:

```python
from spadio.db.models import BaseModel
```

* **BaseModel** – A reusable abstract Django model with common fields.
* **CLI** – Reuse core commands in module management scripts.

> The framework does not run standalone; it is meant to be imported by spadio modules.

---

## Contributing

We welcome contributions!

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

---

## License

spadio is licensed under the **MIT License** – see [LICENSE](LICENSE).

---
