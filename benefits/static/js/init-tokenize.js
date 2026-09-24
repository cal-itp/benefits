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
      display: "show", // omitting this prop results in tokenization failures
      selector: "#cvv",
      title: "Security code",
      placeholder: "123",
    },
  },
  timeoutDuration: 10000,
  validationCallback: function (field, valid, message) {
    const errNode = document.querySelector(`#${field} + p`);
    if (errNode) {
      errNode.innerText = valid ? "" : message;
    }
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
