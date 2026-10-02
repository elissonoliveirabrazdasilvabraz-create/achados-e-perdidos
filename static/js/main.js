document.addEventListener("DOMContentLoaded", () => {

    const imageInput = document.getElementById("image");

    if (imageInput) {

        imageInput.addEventListener("change", () => {

            const file = imageInput.files[0];

            if (!file) {
                return;
            }

            const allowedTypes = [
                "image/jpeg",
                "image/png",
                "image/webp"
            ];

            if (!allowedTypes.includes(file.type)) {

                alert(
                    "Formato de imagem não permitido. " +
                    "Use JPG, PNG ou WEBP."
                );

                imageInput.value = "";

                return;
            }

            const maxSize = 5 * 1024 * 1024;

            if (file.size > maxSize) {

                alert(
                    "A imagem é muito grande. " +
                    "O tamanho máximo permitido é 5 MB."
                );

                imageInput.value = "";

                return;
            }

            showImagePreview(file);
        });
    }


    function showImagePreview(file) {

        let preview = document.getElementById(
            "image-preview"
        );

        if (!preview) {

            preview = document.createElement("div");

            preview.id = "image-preview";

            preview.style.marginTop = "15px";

            imageInput.parentElement.appendChild(
                preview
            );
        }


        preview.innerHTML = "";


        const image = document.createElement("img");

        image.src = URL.createObjectURL(file);

        image.alt = "Pré-visualização da imagem";

        image.style.width = "180px";
        image.style.height = "180px";
        image.style.objectFit = "cover";
        image.style.borderRadius = "8px";
        image.style.border = "1px solid #e2e8f0";


        preview.appendChild(image);
    }

});
