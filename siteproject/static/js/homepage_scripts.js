function toggleModal() {
    const modal = document.getElementById('myModal');
    modal.style.display = (modal.style.display === "block") ? "none" : "block";
}

// Закрытие модального окна при клике вне его области
window.addEventListener("click", function(event) {
    const modal = document.getElementById('myModal');
    const toggleModalBtn = document.querySelector('.modal-btn');

    // Проверка: закрываем модальное окно, если клик вне модального окна и вне кнопки
    if (
        modal.style.display === "block" &&
        !modal.contains(event.target) &&
        event.target !== toggleModalBtn &&
        !toggleModalBtn.contains(event.target) // Проверяем также содержимое кнопки
    ) {
        modal.style.display = "none";
    }
});

function toggleDropdown() {
    const menu = document.getElementById('dropdownMenu');
    menu.style.display = (menu.style.display === "block") ? "none" : "block";
}

// Закрытие модального окна при клике вне его области
window.addEventListener("click", function(event) {
    const menu = document.getElementById('dropdownMenu');
    const toggleDropdownBtn = document.querySelector('.dropdown-btn');

    // Проверка: закрываем модальное окно, если клик вне модального окна и вне кнопки
    if (
        menu.style.display === "block" &&
        !menu.contains(event.target) &&
        event.target !== toggleDropdownBtn &&
        !toggleDropdownBtn.contains(event.target) // Проверяем также содержимое кнопки
    ) {
        menu.style.display = "none";
    }
});

function clearInput() {
    const inputField = document.getElementById("search-input");
    inputField.value = "";
    toggleClearButton();
}


function toggleClearButton() {
    const inputField = document.getElementById("search-input");
    const clearButton = document.querySelector(".clear-btn");
    const searchButton = document.querySelector(".search-btn");

    clearButton.style.display = inputField.value.length > 0 ? "inline-block" : "none";
    searchButton.style.display = inputField.value.length > 0 ? "inline-block" : "none";
}


const toggleFeedbackElements = document.querySelectorAll('.toggleFeedback');
const closeFeedback = document.getElementById('closeFeedback');
const FeedbackModal = document.getElementById('FeedbackModal');


toggleFeedbackElements.forEach(element => {
  element.onclick = function(event) {
    event.preventDefault();
    FeedbackModal.style.display = 'block';
  };
});


closeFeedback.onclick = function() {
  FeedbackModal.style.display = 'none';
}




