(function () {
  const AUTO_FILLED_ATTR = "data-cnpj-autofilled";

  function onlyDigits(value) {
    return String(value || "").replace(/\D/g, "");
  }

  function normalize(value) {
    return String(value || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .trim();
  }

  function getField(id) {
    return document.getElementById(id);
  }

  function dispatchFieldEvents(field) {
    if (!field) {
      return;
    }

    field.dispatchEvent(new Event("input", { bubbles: true }));
    field.dispatchEvent(new Event("change", { bubbles: true }));
  }

  function setFieldValue(field, value, options = {}) {
    if (!field || value === null || value === undefined) {
      return;
    }

    const textValue = String(value).trim();

    if (!textValue) {
      return;
    }

    const force = options.force === true;
    const wasAutoFilled = field.getAttribute(AUTO_FILLED_ATTR) === "true";
    const currentValue = String(field.value || "").trim();

    /*
      Regra:
      - Se o campo estiver vazio, preenche.
      - Se foi preenchido automaticamente antes, pode substituir.
      - Se force=true, substitui.
      - Se o usuário digitou manualmente algo que não veio da consulta, preserva.
    */
    if (!force && currentValue && !wasAutoFilled) {
      return;
    }

    field.value = textValue;
    field.setAttribute(AUTO_FILLED_ATTR, "true");
    dispatchFieldEvents(field);
  }

  function markManualChanges() {
    const fields = [
      "id_nome",
      "id_telefone",
      "id_email",
      "id_cep",
      "id_logradouro",
      "id_numero",
      "id_complemento",
      "id_bairro",
      "id_municipio",
      "id_estado",
    ];

    fields.forEach(function (fieldId) {
      const field = getField(fieldId);

      if (!field) {
        return;
      }

      field.addEventListener("input", function () {
        if (document.activeElement === field) {
          field.removeAttribute(AUTO_FILLED_ATTR);
        }
      });
    });
  }

  function clearAutoFilledFieldsWhenDocumentCleared() {
    const fields = [
      "id_nome",
      "id_telefone",
      "id_email",
      "id_cep",
      "id_logradouro",
      "id_numero",
      "id_complemento",
      "id_bairro",
      "id_municipio",
      "id_estado",
    ];

    fields.forEach(function (fieldId) {
      const field = getField(fieldId);

      if (!field) {
        return;
      }

      const wasAutoFilled = field.getAttribute(AUTO_FILLED_ATTR) === "true";

      if (wasAutoFilled) {
        field.value = "";
        field.removeAttribute(AUTO_FILLED_ATTR);
        dispatchFieldEvents(field);
      }
    });
  }

  function getTipoClienteValue() {
    const tipoField = getField("id_tipo");

    if (!tipoField) {
      return "";
    }

    const selectedOption = tipoField.options[tipoField.selectedIndex];
    const selectedText = selectedOption ? selectedOption.textContent : "";

    return normalize(`${tipoField.value} ${selectedText}`);
  }

  function isPessoaJuridicaSelecionada() {
    const tipo = getTipoClienteValue();

    return (
      tipo.includes("juridica") ||
      tipo.includes("pessoa juridica") ||
      tipo.includes("pj") ||
      tipo.includes("cnpj")
    );
  }

  function getNomeEmpresa(data) {
    const nomeFantasia = String(data.nome_fantasia || "").trim();
    const razaoSocial = String(data.razao_social || "").trim();

    return nomeFantasia || razaoSocial;
  }

  function getTelefoneEmpresa(data) {
    const telefone1 = String(data.ddd_telefone_1 || "").trim();
    const telefone2 = String(data.ddd_telefone_2 || "").trim();

    return telefone1 || telefone2;
  }

  function getFeedbackElement() {
    const documentoField = getField("id_documento");

    if (!documentoField) {
      return null;
    }

    let feedback = document.getElementById("cnpj-lookup-feedback");

    if (!feedback) {
      feedback = document.createElement("small");
      feedback.id = "cnpj-lookup-feedback";
      feedback.style.display = "block";
      feedback.style.marginTop = "8px";
      feedback.style.fontSize = "12px";
      feedback.style.opacity = "0.85";

      documentoField.insertAdjacentElement("afterend", feedback);
    }

    return feedback;
  }

  function setFeedback(message, type = "info") {
    const feedback = getFeedbackElement();

    if (!feedback) {
      return;
    }

    feedback.textContent = message || "";

    if (!message) {
      feedback.style.display = "none";
      return;
    }

    feedback.style.display = "block";

    if (type === "error") {
      feedback.style.color = "#ff7b7b";
    } else if (type === "success") {
      feedback.style.color = "#24c16b";
    } else {
      feedback.style.color = "var(--muted)";
    }
  }

  function preencherCamposComDadosDaEmpresa(data) {
    const nomeField = getField("id_nome");
    const telefoneField = getField("id_telefone");
    const emailField = getField("id_email");

    const cepField = getField("id_cep");
    const logradouroField = getField("id_logradouro");
    const numeroField = getField("id_numero");
    const complementoField = getField("id_complemento");
    const bairroField = getField("id_bairro");
    const municipioField = getField("id_municipio");
    const estadoField = getField("id_estado");

    setFieldValue(nomeField, getNomeEmpresa(data), { force: true });
    setFieldValue(telefoneField, getTelefoneEmpresa(data), { force: true });
    setFieldValue(emailField, data.email, { force: true });

    setFieldValue(cepField, data.cep, { force: true });
    setFieldValue(logradouroField, data.logradouro, { force: true });
    setFieldValue(numeroField, data.numero, { force: true });
    setFieldValue(complementoField, data.complemento, { force: true });
    setFieldValue(bairroField, data.bairro, { force: true });
    setFieldValue(municipioField, data.municipio, { force: true });
    setFieldValue(estadoField, data.uf, { force: true });
  }

  async function consultarCnpj(cnpj) {
    const response = await fetch(`https://brasilapi.com.br/api/cnpj/v1/${cnpj}`);

    if (!response.ok) {
      throw new Error("CNPJ não encontrado.");
    }

    return response.json();
  }

  let ultimoCnpjConsultado = "";
  let consultaEmAndamento = false;

  async function handleDocumentoLookup() {
    const documentoField = getField("id_documento");

    if (!documentoField) {
      return;
    }

    const cnpj = onlyDigits(documentoField.value);

    if (!isPessoaJuridicaSelecionada()) {
      setFeedback("");
      return;
    }

    if (cnpj.length === 0) {
      ultimoCnpjConsultado = "";
      clearAutoFilledFieldsWhenDocumentCleared();
      setFeedback("");
      return;
    }

    if (cnpj.length !== 14) {
      setFeedback("Digite um CNPJ válido com 14 números.", "error");
      return;
    }

    if (consultaEmAndamento) {
      return;
    }

    if (cnpj === ultimoCnpjConsultado) {
      return;
    }

    try {
      consultaEmAndamento = true;
      ultimoCnpjConsultado = cnpj;

      setFeedback("Consultando CNPJ...", "info");

      const data = await consultarCnpj(cnpj);

      preencherCamposComDadosDaEmpresa(data);

      setFeedback("CNPJ encontrado. Dados preenchidos automaticamente.", "success");
    } catch (error) {
      setFeedback("Não foi possível consultar este CNPJ. Preencha os dados manualmente.", "error");
    } finally {
      consultaEmAndamento = false;
    }
  }

  function bindCnpjLookup() {
    const tipoField = getField("id_tipo");
    const documentoField = getField("id_documento");

    if (!documentoField) {
      return;
    }

    markManualChanges();

    documentoField.addEventListener("blur", handleDocumentoLookup);

    documentoField.addEventListener("input", function () {
      const cnpj = onlyDigits(documentoField.value);

      if (cnpj.length < 14) {
        ultimoCnpjConsultado = "";
      }

      if (cnpj.length === 0) {
        clearAutoFilledFieldsWhenDocumentCleared();
        setFeedback("");
        return;
      }

      if (cnpj.length === 14 && isPessoaJuridicaSelecionada()) {
        window.clearTimeout(documentoField.cnpjLookupTimeout);

        documentoField.cnpjLookupTimeout = window.setTimeout(function () {
          handleDocumentoLookup();
        }, 500);
      }
    });

    if (tipoField) {
      tipoField.addEventListener("change", function () {
        ultimoCnpjConsultado = "";
        handleDocumentoLookup();
      });
    }
  }

  document.addEventListener("DOMContentLoaded", bindCnpjLookup);
})();