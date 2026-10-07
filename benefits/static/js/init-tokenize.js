const errInfoSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">
          <path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM13 17H11V15H13V17ZM13 13H11V7H13V13Z" fill="#DE0E10" />
        </svg>`;

// we substitute a single custom error message per field so that we can translate it
const errMap = {
  ccnumber:
    errInfoSvg +
    " Please enter a valid credit card number from Visa, Discover or Mastercard.",
  ccexp: errInfoSvg + " Please enter an expiration date in a MM/YY format.",
};

const errColor = "#de0e10";

const opts = {
  paymentSelector: "#tokenizeButton",
  variant: "inline",
  invalidCss: {
    color: errColor,
    "border-color": errColor,
  },
  fields: {
    ccnumber: {
      selector: "#ccnumber",
      placeholder: "1111 1111 1111 1111",
      enableCardBrandPreviews: "true",
    },
    ccexp: {
      selector: "#ccexp",
      title: "Expiration date",
      placeholder: "MM / YY",
    },
    cvv: {
      display: "show", // omitting this prop results in tokenization failure
      selector: "#cvv",
      title: "Security code",
      placeholder: "123",
    },
  },
  timeoutDuration: 10000,
  validationCallback: function (field, valid) {
    const errNode = document.querySelector(`#${field} + .cjs-error`);
    if (!errNode) return;

    errNode.innerHTML = valid ? "" : errMap[field];
  },
  timeoutCallback: function () {
    console.error(
      "Tokenization didn't complete in the expected timeframe. This could be due to an invalid or incomplete field or poor connectivity",
    );
  },
  callback: function (response) {
    document.querySelector("#tokenized-card").value = response.token;
    document.querySelector("#tokenization-form").submit();
  },
};

document.addEventListener("DOMContentLoaded", function () {
  CollectJS.configure(opts);
});
