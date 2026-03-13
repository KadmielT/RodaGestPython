document.addEventListener("DOMContentLoaded", function () {

    const telefoneField = document.getElementById("id_telefone");

    if (!telefoneField) return;

    function aplicarMascaraTelefone(valor) {

        valor = valor.replace(/\D/g, "");
        valor = valor.slice(0, 11);

        if (valor.length <= 10) {

            valor = valor.replace(/^(\d{2})(\d)/g, "($1) $2");
            valor = valor.replace(/(\d{4})(\d)/, "$1-$2");

        } else {

            valor = valor.replace(/^(\d{2})(\d)/g, "($1) $2");
            valor = valor.replace(/(\d{5})(\d)/, "$1-$2");

        }

        return valor;
    }

    telefoneField.addEventListener("input", function () {
        telefoneField.value = aplicarMascaraTelefone(telefoneField.value);
    });

});