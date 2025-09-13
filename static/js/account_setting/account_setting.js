const tbody = document.querySelector("tbody");
new Sortable(tbody, {
  animation: 150,
  onEnd: function () {
    const order = [];
    document
      .querySelectorAll("tbody tr")
      .forEach((tr) => order.push(tr.dataset.id));
    fetch("/account_setting/reorder", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ order }),
    });
  },
});

function updateAccount(accountId) {
  const row = event.target.closest("tr");
  const inputs = row.querySelectorAll("input, select");
  const formData = new FormData();
  inputs.forEach((el) => formData.append(el.dataset.field, el.value));
  fetch(`/account_setting/update/${accountId}`, {
    method: "POST",
    body: formData,
  }).then((res) => {
    if (!res.ok) alert("수정 실패");
  });
}

function confirmDelete() {
  return confirm("정말 삭제하시겠습니까?");
}
