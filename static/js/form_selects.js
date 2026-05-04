document.addEventListener("DOMContentLoaded", function () {
  if (typeof TomSelect === "undefined") {
    return;
  }

  const selects = document.querySelectorAll(".js-tom-select");

  selects.forEach(function (select) {
    if (select.tomselect) {
      return;
    }

    new TomSelect(select, {
      create: false,
      allowEmptyOption: true,
      maxOptions: null,
      sortField: {
        field: "$order",
        direction: "asc"
      }
    });
  });
});