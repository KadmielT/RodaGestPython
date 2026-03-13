document.addEventListener("DOMContentLoaded", function () {
    const tipoField = document.getElementById("id_tipo");
    const documentoField = document.getElementById("id_documento");

    if (!tipoField || !documentoField) return;

    function somenteNumeros(valor) {
        return valor.replace(/\D/g, "");
    }

    function aplicarMascaraCPF(valor) {
        valor = somenteNumeros(valor).slice(0, 11);

        valor = valor.replace(/(\d{3})(\d)/, "$1.$2");
        valor = valor.replace(/(\d{3})(\d)/, "$1.$2");
        valor = valor.replace(/(\d{3})(\d{1,2})$/, "$1-$2");

        return valor;
    }

    function aplicarMascaraCNPJ(valor) {
        valor = somenteNumeros(valor).slice(0, 14);

        valor = valor.replace(/^(\d{2})(\d)/, "$1.$2");
        valor = valor.replace(/^(\d{2})\.(\d{3})(\d)/, "$1.$2.$3");
        valor = valor.replace(/\.(\d{3})(\d)/, ".$1/$2");
        valor = valor.replace(/(\d{4})(\d)/, "$1-$2");

        return valor;
    }

    function atualizarPlaceholderEMaxlength() {
        if (tipoField.value === "PF") {
            documentoField.placeholder = "000.000.000-00";
            documentoField.maxLength = 14;
        } else if (tipoField.value === "PJ") {
            documentoField.placeholder = "00.000.000/0000-00";
            documentoField.maxLength = 18;
        } else {
            documentoField.placeholder = "Digite o CPF ou CNPJ";
            documentoField.maxLength = 18;
        }
    }

    function aplicarMascaraAtual() {
        const valor = documentoField.value;

        if (tipoField.value === "PF") {
            documentoField.value = aplicarMascaraCPF(valor);
        } else if (tipoField.value === "PJ") {
            documentoField.value = aplicarMascaraCNPJ(valor);
        }
    }

    tipoField.addEventListener("change", function () {
        documentoField.value = "";
        atualizarPlaceholderEMaxlength();
    });

    documentoField.addEventListener("input", function () {
        aplicarMascaraAtual();
    });

    atualizarPlaceholderEMaxlength();
    aplicarMascaraAtual();
});