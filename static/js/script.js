let allMenuItems = [];
let categories = [];

document.addEventListener("DOMContentLoaded", () => {
  fetchCategories();
  fetchMenuItems();

  document
    .getElementById("apply-filters")
    .addEventListener("click", applyFilters);
  document
    .getElementById("search-input")
    .addEventListener("input", applyFilters);
  document
    .getElementById("sort-select")
    .addEventListener("change", applyFilters);
});

async function fetchCategories() {
  const response = await fetch("/api/categories");
  categories = await response.json();
  const categoryFilters = document.getElementById("category-filters");
  categories.forEach((category) => {
    categoryFilters.innerHTML += `
            <div class="filter-group">
                <label>
                    <input type="checkbox" name="category" value="${category.CategoryID}">
                    ${category.CategoryName}
                </label>
            </div>
        `;
  });
}

async function fetchMenuItems() {
  const response = await fetch("/api/menu_items");
  allMenuItems = await response.json();
  renderMenuItems(allMenuItems);
}

function renderMenuItems(menuItems) {
  const menuItemsContainer = document.getElementById("menu-items-container");
  menuItemsContainer.innerHTML = "";
  menuItems.forEach((item) => {
    menuItemsContainer.innerHTML += `
            <div class="menu-item">
                <img src="${
                  item.ImageURL || "/static/images/placeholder.jpg"
                }" alt="${item.Name}">
                <h3>${item.Name}</h3>
                <p>${item.Description}</p>
                <p class="price">$${item.Price.toFixed(2)}</p>
                <p class="category">${item.CategoryName}</p>
            </div>
        `;
  });
}

function applyFilters() {
  const selectedCategories = Array.from(
    document.querySelectorAll('input[name="category"]:checked')
  ).map((el) => el.value);
  const searchTerm = document
    .getElementById("search-input")
    .value.toLowerCase();
  const sortOption = document.getElementById("sort-select").value;

  let filteredItems = allMenuItems.filter((item) => {
    const matchesCategory =
      selectedCategories.length === 0 ||
      selectedCategories.includes(item.CategoryID.toString());
    const matchesSearch =
      item.Name.toLowerCase().includes(searchTerm) ||
      item.Description.toLowerCase().includes(searchTerm);
    return matchesCategory && matchesSearch;
  });

  // Sort the filtered items
  filteredItems.sort((a, b) => {
    switch (sortOption) {
      case "name-asc":
        return a.Name.localeCompare(b.Name);
      case "name-desc":
        return b.Name.localeCompare(a.Name);
      case "price-asc":
        return a.Price - b.Price;
      case "price-desc":
        return b.Price - a.Price;
      default:
        return 0;
    }
  });

  renderMenuItems(filteredItems);
}
