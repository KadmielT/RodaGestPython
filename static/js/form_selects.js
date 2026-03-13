document.addEventListener("DOMContentLoaded", function () {
  const campoTipo = document.querySelector("#id_tipo");

  if (campoTipo) {
    new TomSelect(campoTipo, {
      create: false,
      allowEmptyOption: true
    });
  }
});