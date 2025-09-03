const API_URL = "<API endpoint>/images";

document.getElementById("datePicker").addEventListener("change", async (e) => {
  const date = e.target.value;
  const response = await fetch(`${API_URL}?date=${date}`);
  const data = await response.json();

  const gallery = document.getElementById("gallery");
  gallery.innerHTML = "";
  data.images.forEach(url => {
    const img = document.createElement("img");
    img.src = url;
    gallery.appendChild(img);
  });
});
