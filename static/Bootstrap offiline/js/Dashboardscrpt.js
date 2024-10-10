//Wrapper
var el = document.getElementById("wrapper");
var toggleButton = document.getElementById("menu-toggle");

toggleButton.onclick = function () {
    el.classList.toggle("toggled");
};
//Wrapper

//RECHARGE functions
function toggleCardFields() {
    const cardOption = document.getElementById('cardOption').value;
    const cardField = document.getElementById('cardField');

    // Show relevant fields based on the selected option
    if (cardOption === 'card') {
        cardField.style.display = 'block'; // Show the card fields
    } else {
        cardField.style.display = 'none'; // Hide the card fields
    }
}
//RECHARGE

//BANK
function toggleBankFields() {
    const bankSelect = document.getElementById("bankOption");
    const bankField = document.getElementById("bankField");
    // Check if a bank is selected
    if (bankSelect.value) {
        bankField.style.display = "block"; // Show bank fields
    } else {
        bankField.style.display = "none"; // Hide bank fields
    }
}
//BANK