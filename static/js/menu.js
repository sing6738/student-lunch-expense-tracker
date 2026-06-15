(function () {
  const restaurantSelect = document.getElementById("restaurantSelect");
  const menuSelect = document.getElementById("menuSelect");
  const priceInput = document.getElementById("priceInput");
  const menusByRestaurant = window.menusByRestaurant || {};

  if (!restaurantSelect || !menuSelect || !priceInput) {
    return;
  }

  function renderMenus(keepSelected) {
    const restaurantId = restaurantSelect.value;
    const menus = menusByRestaurant[restaurantId] || [];
    const selectedMenuId = keepSelected ? String(window.selectedMenuId || menuSelect.value) : "";

    menuSelect.innerHTML = "";
    menus.forEach((menu) => {
      const option = document.createElement("option");
      option.value = menu.id;
      option.textContent = menu.name;
      option.dataset.price = menu.price;
      if (String(menu.id) === selectedMenuId) {
        option.selected = true;
      }
      menuSelect.appendChild(option);
    });

    fillPrice();
  }

  function fillPrice() {
    const option = menuSelect.options[menuSelect.selectedIndex];
    if (option) {
      priceInput.value = Number(option.dataset.price || 0).toFixed(2);
    }
  }

  restaurantSelect.addEventListener("change", () => renderMenus(false));
  menuSelect.addEventListener("change", fillPrice);
  renderMenus(true);
})();
