from datetime import datetime
from pathlib import Path
from uuid import uuid4

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from werkzeug.utils import secure_filename


# ============================================================
# CONFIGURAÇÃO
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

INSTANCE_DIR = BASE_DIR / "instance"
UPLOAD_DIR = BASE_DIR / "static" / "uploads"

INSTANCE_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


app = Flask(__name__)

app.config["SECRET_KEY"] = "achados-perdidos-chave-desenvolvimento"

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{INSTANCE_DIR / 'achados_perdidos.db'}"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["UPLOAD_FOLDER"] = str(UPLOAD_DIR)

# Limite máximo de upload: 5 MB
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024


db = SQLAlchemy(app)


# ============================================================
# CONFIGURAÇÕES DE UPLOAD
# ============================================================

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp",
}


def allowed_file(filename):
    """
    Verifica se a extensão do arquivo é permitida.
    """

    if not filename or "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()

    return extension in ALLOWED_EXTENSIONS


def save_image(file):
    """
    Salva a imagem enviada pelo usuário com um nome único.
    """

    if not file or not file.filename:
        return None

    if not allowed_file(file.filename):
        return None

    filename = secure_filename(file.filename)

    extension = Path(filename).suffix.lower()

    unique_filename = f"{uuid4().hex}{extension}"

    destination = UPLOAD_DIR / unique_filename

    file.save(destination)

    return unique_filename


def delete_image(filename):
    """
    Remove uma imagem existente.
    """

    if not filename:
        return

    file_path = UPLOAD_DIR / filename

    if file_path.exists():
        file_path.unlink()


# ============================================================
# MODELO DO BANCO
# ============================================================

class Item(db.Model):

    __tablename__ = "items"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(120),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    item_type = db.Column(
        db.String(20),
        nullable=False
    )

    location = db.Column(
        db.String(200),
        nullable=False
    )

    date = db.Column(
        db.Date,
        nullable=False
    )

    contact_name = db.Column(
        db.String(120),
        nullable=False
    )

    contact = db.Column(
        db.String(120),
        nullable=False
    )

    image_filename = db.Column(
        db.String(255),
        nullable=True
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="aberto"
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


# ============================================================
# PÁGINA PRINCIPAL
# ============================================================

@app.route("/")
def index():

    search = request.args.get(
        "search",
        ""
    ).strip()

    item_type = request.args.get(
        "item_type",
        ""
    ).strip()

    status = request.args.get(
        "status",
        ""
    ).strip()

    query = Item.query


    # --------------------------------------------------------
    # BUSCA
    # --------------------------------------------------------

    if search:

        search_term = f"%{search}%"

        query = query.filter(
            or_(
                Item.title.ilike(search_term),
                Item.description.ilike(search_term),
                Item.location.ilike(search_term)
            )
        )


    # --------------------------------------------------------
    # FILTRO POR TIPO
    # --------------------------------------------------------

    if item_type in {
        "perdido",
        "encontrado"
    }:

        query = query.filter(
            Item.item_type == item_type
        )


    # --------------------------------------------------------
    # FILTRO POR STATUS
    # --------------------------------------------------------

    if status in {
        "aberto",
        "devolvido"
    }:

        query = query.filter(
            Item.status == status
        )


    # --------------------------------------------------------
    # RESULTADOS
    # --------------------------------------------------------

    items = (
        query
        .order_by(
            Item.created_at.desc()
        )
        .all()
    )


    return render_template(
        "index.html",
        items=items,
        search=search,
        item_type=item_type,
        status=status
    )


# ============================================================
# NOVO ITEM
# ============================================================

@app.route("/item/novo")
def new_item():

    return render_template(
        "item_form.html"
    )


# ============================================================
# CRIAR ITEM
# ============================================================

@app.route(
    "/item/criar",
    methods=["POST"]
)
def create_item():

    item_type = request.form.get(
        "item_type",
        ""
    ).strip()

    title = request.form.get(
        "title",
        ""
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()

    location = request.form.get(
        "location",
        ""
    ).strip()

    date_text = request.form.get(
        "date",
        ""
    ).strip()

    contact_name = request.form.get(
        "contact_name",
        ""
    ).strip()

    contact = request.form.get(
        "contact",
        ""
    ).strip()


    # --------------------------------------------------------
    # VALIDAÇÃO
    # --------------------------------------------------------

    if not all([
        item_type,
        title,
        description,
        location,
        date_text,
        contact_name,
        contact,
    ]):

        flash(
            "Preencha todos os campos obrigatórios.",
            "error"
        )

        return redirect(
            url_for("new_item")
        )


    if item_type not in {
        "perdido",
        "encontrado"
    }:

        flash(
            "Tipo de item inválido.",
            "error"
        )

        return redirect(
            url_for("new_item")
        )


    # --------------------------------------------------------
    # DATA
    # --------------------------------------------------------

    try:

        item_date = datetime.strptime(
            date_text,
            "%Y-%m-%d"
        ).date()

    except ValueError:

        flash(
            "A data informada é inválida.",
            "error"
        )

        return redirect(
            url_for("new_item")
        )


    # --------------------------------------------------------
    # IMAGEM
    # --------------------------------------------------------

    image = request.files.get(
        "image"
    )

    image_filename = None


    if image and image.filename:

        if not allowed_file(
            image.filename
        ):

            flash(
                "Formato de imagem inválido. "
                "Use JPG, PNG ou WEBP.",
                "error"
            )

            return redirect(
                url_for("new_item")
            )


        image_filename = save_image(
            image
        )


    # --------------------------------------------------------
    # CRIA ITEM
    # --------------------------------------------------------

    item = Item(

        title=title,

        description=description,

        item_type=item_type,

        location=location,

        date=item_date,

        contact_name=contact_name,

        contact=contact,

        image_filename=image_filename,

        status="aberto",
    )


    db.session.add(item)

    db.session.commit()


    flash(
        "Item cadastrado com sucesso!",
        "success"
    )


    return redirect(
        url_for(
            "item_detail",
            item_id=item.id
        )
    )


# ============================================================
# DETALHES
# ============================================================

@app.route(
    "/item/<int:item_id>"
)
def item_detail(item_id):

    item = db.get_or_404(
        Item,
        item_id
    )

    return render_template(
        "item_detail.html",
        item=item
    )


# ============================================================
# EDITAR ITEM
# ============================================================

@app.route(
    "/item/<int:item_id>/editar",
    methods=["GET", "POST"]
)
def edit_item(item_id):

    item = db.get_or_404(
        Item,
        item_id
    )


    # --------------------------------------------------------
    # EXIBIR FORMULÁRIO
    # --------------------------------------------------------

    if request.method == "GET":

        return render_template(
            "item_form.html",
            item=item,
            editing=True
        )


    # --------------------------------------------------------
    # RECEBER FORMULÁRIO
    # --------------------------------------------------------

    item_type = request.form.get(
        "item_type",
        ""
    ).strip()

    title = request.form.get(
        "title",
        ""
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()

    location = request.form.get(
        "location",
        ""
    ).strip()

    date_text = request.form.get(
        "date",
        ""
    ).strip()

    contact_name = request.form.get(
        "contact_name",
        ""
    ).strip()

    contact = request.form.get(
        "contact",
        ""
    ).strip()


    if not all([
        item_type,
        title,
        description,
        location,
        date_text,
        contact_name,
        contact,
    ]):

        flash(
            "Preencha todos os campos obrigatórios.",
            "error"
        )

        return redirect(
            url_for(
                "edit_item",
                item_id=item.id
            )
        )


    if item_type not in {
        "perdido",
        "encontrado"
    }:

        flash(
            "Tipo de item inválido.",
            "error"
        )

        return redirect(
            url_for(
                "edit_item",
                item_id=item.id
            )
        )


    try:

        item_date = datetime.strptime(
            date_text,
            "%Y-%m-%d"
        ).date()

    except ValueError:

        flash(
            "A data informada é inválida.",
            "error"
        )

        return redirect(
            url_for(
                "edit_item",
                item_id=item.id
            )
        )


    # --------------------------------------------------------
    # ATUALIZA DADOS
    # --------------------------------------------------------

    item.item_type = item_type
    item.title = title
    item.description = description
    item.location = location
    item.date = item_date
    item.contact_name = contact_name
    item.contact = contact


    # --------------------------------------------------------
    # NOVA IMAGEM
    # --------------------------------------------------------

    image = request.files.get(
        "image"
    )


    if image and image.filename:

        if not allowed_file(
            image.filename
        ):

            flash(
                "Formato de imagem inválido.",
                "error"
            )

            return redirect(
                url_for(
                    "edit_item",
                    item_id=item.id
                )
            )


        old_image = item.image_filename

        item.image_filename = save_image(
            image
        )

        delete_image(
            old_image
        )


    db.session.commit()


    flash(
        "Item atualizado com sucesso!",
        "success"
    )


    return redirect(
        url_for(
            "item_detail",
            item_id=item.id
        )
    )


# ============================================================
# MARCAR COMO DEVOLVIDO
# ============================================================

@app.route(
    "/item/<int:item_id>/devolver",
    methods=["POST"]
)
def mark_as_returned(item_id):

    item = db.get_or_404(
        Item,
        item_id
    )


    if item.status == "devolvido":

        flash(
            "Este item já está marcado como devolvido.",
            "error"
        )

        return redirect(
            url_for(
                "item_detail",
                item_id=item.id
            )
        )


    item.status = "devolvido"

    db.session.commit()


    flash(
        "Item marcado como devolvido!",
        "success"
    )


    return redirect(
        url_for(
            "item_detail",
            item_id=item.id
        )
    )


# ============================================================
# REABRIR ITEM
# ============================================================

@app.route(
    "/item/<int:item_id>/reabrir",
    methods=["POST"]
)
def reopen_item(item_id):

    item = db.get_or_404(
        Item,
        item_id
    )

    item.status = "aberto"

    db.session.commit()


    flash(
        "Item reaberto.",
        "success"
    )


    return redirect(
        url_for(
            "item_detail",
            item_id=item.id
        )
    )


# ============================================================
# EXCLUIR ITEM
# ============================================================

@app.route(
    "/item/<int:item_id>/excluir",
    methods=["POST"]
)
def delete_item(item_id):

    item = db.get_or_404(
        Item,
        item_id
    )


    image_filename = item.image_filename


    db.session.delete(item)

    db.session.commit()


    delete_image(
        image_filename
    )


    flash(
        "Item excluído com sucesso.",
        "success"
    )


    return redirect(
        url_for("index")
    )


# ============================================================
# TRATAMENTO DE ARQUIVO GRANDE
# ============================================================

@app.errorhandler(413)
def request_entity_too_large(error):

    flash(
        "A imagem é muito grande. "
        "O tamanho máximo permitido é 5 MB.",
        "error"
    )

    return redirect(
        url_for("new_item")
    )


# ============================================================
# INICIALIZAÇÃO DO BANCO
# ============================================================

with app.app_context():

    db.create_all()


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )
