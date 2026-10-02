# Achados e Perdidos

Aplicação web simples para criar um mural de objetos perdidos e encontrados.

O sistema foi desenvolvido com:

- Python
- Flask
- SQLite
- Flask-SQLAlchemy
- HTML5
- CSS3
- JavaScript

## Funcionalidades

- Visualização dos itens cadastrados no mural
- Cadastro de itens perdidos
- Cadastro de itens encontrados
- Informações sobre o item
- Local onde o item foi perdido/encontrado
- Data do ocorrido
- Descrição
- Informações de contato
- Upload de imagem
- Visualização dos detalhes de um item
- Controle do status do item

## Estrutura do projeto

```text
achados-perdidos/
├── app.py
├── requirements.txt
├── README.md
├── instance/
│   └── achados_perdidos.db
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── item_form.html
│   └── item_detail.html
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── uploads/
└── .gitignore
