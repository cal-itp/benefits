const timeoutMsg =
  "Tokenization didn't complete in the expected timeframe.  This could be due to an invalid or incomplete field or poor connectivity";

const opts = {
  paymentSelector: "#tokenizeButton",
  variant: "inline",
  invalidCss: {
    color: "#de0e10",
    "border-color": "#de0e10",
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
      display: "show",
      selector: "#cvv",
      title: "Security code",
      placeholder: "123",
    },
  },
  validationCallback: function (field, valid, message) {
    const errNode = document.querySelector(`#${field} + p`);
    errNode.innerText = valid ? "" : message;
  },
  timeoutDuration: 10000,
  timeoutCallback: function () {
    console.error(timeoutMsg);
  },
  callback: function (response, foo) {
    document.querySelector("#tokenized-card").value = response.token;
    document.querySelector("#tokenization-form").submit();
  },
};

document.addEventListener("DOMContentLoaded", function () {
  CollectJS.configure(opts);
});
