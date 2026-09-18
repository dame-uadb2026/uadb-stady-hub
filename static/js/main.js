// UADB Study Hub — comportements légers côté client
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".alerte").forEach((alerte) => {
    setTimeout(() => {
      alerte.style.transition = "opacity 0.4s ease";
      alerte.style.opacity = "0";
      setTimeout(() => alerte.remove(), 400);
    }, 4500);
  });
});
