function setupPasswordToggle(button, input) {
  if (!button || !input || button.dataset.passwordToggleBound === "true") {
    return;
  }

  button.dataset.passwordToggleBound = "true";

  button.addEventListener("click", function () {
    const isPassword = input.type === "password";

    input.type = isPassword ? "text" : "password";

    const showLabel = button.dataset.showLabel || button.getAttribute("aria-label") || "Mostrar senha";
    const hideLabel = button.dataset.hideLabel || "Ocultar senha";

    button.setAttribute(
      "aria-label",
      isPassword ? hideLabel : showLabel
    );

    button.setAttribute(
      "aria-pressed",
      isPassword ? "true" : "false"
    );
  });
}

function initPasswordToggles() {
  const buttonsByData = document.querySelectorAll("[data-password-toggle]");

  buttonsByData.forEach(function (button) {
    const inputId = button.dataset.passwordToggle;
    const input = document.getElementById(inputId);

    setupPasswordToggle(button, input);
  });

  const legacyPairs = [
    {
      buttonId: "togglePassword",
      inputId: "id_password",
      showLabel: "Mostrar senha",
      hideLabel: "Ocultar senha",
    },
    {
      buttonId: "toggleOldPassword",
      inputId: "id_old_password",
      showLabel: "Mostrar senha atual",
      hideLabel: "Ocultar senha atual",
    },
    {
      buttonId: "toggleNewPassword1",
      inputId: "id_new_password1",
      showLabel: "Mostrar nova senha",
      hideLabel: "Ocultar nova senha",
    },
    {
      buttonId: "toggleNewPassword2",
      inputId: "id_new_password2",
      showLabel: "Mostrar confirmação da senha",
      hideLabel: "Ocultar confirmação da senha",
    },
  ];

  legacyPairs.forEach(function (pair) {
    const button = document.getElementById(pair.buttonId);
    const input = document.getElementById(pair.inputId);

    if (!button || !input) {
      return;
    }

    button.dataset.showLabel = pair.showLabel;
    button.dataset.hideLabel = pair.hideLabel;

    setupPasswordToggle(button, input);
  });
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function clearPasswordFormErrors(form) {
  const feedback = form.querySelector("[data-password-feedback]");
  const fieldErrors = form.querySelectorAll("[data-password-error]");

  if (feedback) {
    feedback.hidden = true;
    feedback.textContent = "";
  }

  fieldErrors.forEach(function (errorElement) {
    errorElement.hidden = true;
    errorElement.innerHTML = "";
  });
}

function showPasswordFeedback(form, message) {
  const feedback = form.querySelector("[data-password-feedback]");

  if (!feedback) {
    return;
  }

  feedback.textContent = message || "Não foi possível alterar sua senha.";
  feedback.hidden = false;
}

function showPasswordFieldErrors(form, errors) {
  if (!errors) {
    return;
  }

  Object.keys(errors).forEach(function (fieldName) {
    const errorElement = form.querySelector(`[data-password-error="${fieldName}"]`);

    if (!errorElement) {
      return;
    }

    const messages = errors[fieldName];

    if (!messages || messages.length === 0) {
      return;
    }

    errorElement.innerHTML = messages.map(escapeHtml).join("<br>");
    errorElement.hidden = false;
  });

  if (errors.__all__) {
    showPasswordFeedback(form, errors.__all__.join(" "));
  }
}

function initPasswordChangeAjax() {
  const form = document.querySelector("[data-password-change-form]");

  if (!form) {
    return;
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();

    clearPasswordFormErrors(form);

    const submitButton = form.querySelector('button[type="submit"]');
    const originalButtonText = submitButton ? submitButton.textContent : "";

    if (submitButton) {
      submitButton.disabled = true;
      submitButton.textContent = "Alterando...";
    }

    fetch(form.action || window.location.href, {
      method: "POST",
      body: new FormData(form),
      credentials: "same-origin",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
    })
      .then(function (response) {
        return response.json().then(function (data) {
          return {
            ok: response.ok,
            data: data,
          };
        });
      })
      .then(function (result) {
        if (result.ok && result.data.success) {
          window.location.href = result.data.redirect_url || window.location.href;
          return;
        }

        showPasswordFeedback(
          form,
          result.data.message || "Não foi possível alterar sua senha. Revise os campos informados."
        );

        showPasswordFieldErrors(form, result.data.errors);
      })
      .catch(function () {
        showPasswordFeedback(
          form,
          "Não foi possível alterar sua senha agora. Tente novamente."
        );
      })
      .finally(function () {
        if (submitButton) {
          submitButton.disabled = false;
          submitButton.textContent = originalButtonText;
        }
      });
  });
}

function initPasswordHelpers() {
  initPasswordToggles();
  initPasswordChangeAjax();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initPasswordHelpers);
} else {
  initPasswordHelpers();
}