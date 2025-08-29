document.addEventListener("DOMContentLoaded", () => {
  fetch("images.json")
    .then(response => response.json())
    .then(data => {
      const gallery = document.getElementById("gallery");

      data.images.forEach(img => {
        const imgElement = document.createElement("img");
        imgElement.src = img.url;
        imgElement.alt = img.caption || "College Image";
        gallery.appendChild(imgElement);
      });
    })
    .catch(error => console.error("Error loading images:", error));
});
