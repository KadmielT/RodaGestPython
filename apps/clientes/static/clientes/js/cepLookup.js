document.addEventListener("DOMContentLoaded", function () {
  console.log("cepLookup carregado");

  const cepInput = document.getElementById("id_cep");
  const logradouroInput = document.getElementById("id_logradouro");
  const bairroInput = document.getElementById("id_bairro");
  const municipioInput = document.getElementById("id_municipio");
  const estadoInput = document.getElementById("id_estado");

  console.log("Campos encontrados:", {
    cepInput,
    logradouroInput,
    bairroInput,
    municipioInput,
    estadoInput
  });

  if (!cepInput) return;

  function limparCep(valor) {
    return valor.replace(/\D/g, "");
  }

  function formatarCep(valor) {
    const cep = limparCep(valor).slice(0, 8);

    if (cep.length <= 5) {
      return cep;
    }

    return cep.slice(0, 5) + "-" + cep.slice(5);
  }

  function preencherEndereco(dados) {
    console.log("Dados recebidos do ViaCEP:", dados);

    if (logradouroInput && !logradouroInput.value) {
      logradouroInput.value = dados.logradouro || "";
    }

    if (bairroInput && !bairroInput.value) {
      bairroInput.value = dados.bairro || "";
    }

    if (municipioInput && !municipioInput.value) {
      municipioInput.value = dados.localidade || "";
    }

    if (estadoInput && !estadoInput.value) {
      estadoInput.value = dados.uf || "";
    }
  }

  function limparEndereco() {
    if (logradouroInput) logradouroInput.value = "";
    if (bairroInput) bairroInput.value = "";
    if (municipioInput) municipioInput.value = "";
    if (estadoInput) estadoInput.value = "";
  }

  async function buscarCep(cep) {
    try {
      console.log("Buscando CEP:", cep);

      const response = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
      console.log("Status da resposta:", response.status);

      if (!response.ok) {
        throw new Error("CEP inválido");
      }

      const dados = await response.json();

      if (dados.erro) {
        alert("CEP não encontrado.");
        limparEndereco();
        return;
      }

      preencherEndereco(dados);

    } catch (error) {
      console.error("Erro ao buscar CEP:", error);
      alert("Erro ao buscar CEP.");
    }
  }

  cepInput.addEventListener("input", function (e) {
    e.target.value = formatarCep(e.target.value);
  });

  cepInput.addEventListener("blur", function () {
    const cepLimpo = limparCep(cepInput.value);
    console.log("Blur no CEP, valor limpo:", cepLimpo);

    if (cepLimpo.length !== 8) {
      console.log("CEP com tamanho inválido");
      return;
    }

    buscarCep(cepLimpo);
  });
});