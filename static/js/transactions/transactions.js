function updateTransaction(transactionId) {
  const row = event.target.closest("tr");
  const inputs = row.querySelectorAll("input, select");
  const formData = new FormData();

  inputs.forEach((el) => {
    formData.append(el.dataset.field, el.value);
  });

  fetch(`/transactions/update/${transactionId}`, {
    method: "POST",
    body: formData,
  }).then((res) => {
    if (!res.ok) {
      alert("거래 수정 실패");
    }
  });
}
document.addEventListener("DOMContentLoaded", function () {
  const priceInput = document.querySelector('input[name="price"]');
  const quantityInput = document.querySelector('input[name="quantity"]');
  const feeInput = document.querySelector('input[name="fee"]');
  const amountInput = document.querySelector('input[name="amount"]');
  const typeSelect = document.querySelector('select[name="type"]');

  function updateAmount() {
    const price = parseFloat(priceInput.value) || 0;
    const quantity = parseFloat(quantityInput.value) || 0;
    const fee = parseFloat(feeInput.value) || 0;
    let amount = price * quantity;

    const type = typeSelect.value;
    if (type === TransactionTypes.BUY) {
      amount += fee;
    } else if (type === TransactionTypes.SELL) {
      amount -= fee;
    }
    amountInput.value = amount.toFixed(2);
  }

  [priceInput, quantityInput, feeInput, typeSelect].forEach((input) => {
    input.addEventListener("input", updateAmount);
  });

  const form = document.getElementById("transaction-form");
  if (!form) {
    console.error("transaction-form not found!");
    return;
  }

  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    const formData = new FormData(this);
    try {
      const response = await fetch("/transactions/add", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();
      console.log(result);

      if (result.status === "ok") {
        this.reset();
        window.location.reload();
      } else {
        alert("거래 추가 실패!");
      }
    } catch (err) {
      console.error("요청 실패:", err);
      alert("에러 발생!");
    }
  });
});
