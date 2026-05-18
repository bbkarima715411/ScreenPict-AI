const photoInput = document.querySelector("#photo-input");
const localPreview = document.querySelector("#local-preview");
const analysisForm = document.querySelector("#analysis-form");
const analysisProgress = document.querySelector("#analysis-progress");
const deleteModal = document.querySelector("#delete-modal");
const cancelDeleteButton = document.querySelector("#cancel-delete");
const confirmDeleteButton = document.querySelector("#confirm-delete");
let pendingDeleteForm = null;

photoInput?.addEventListener("change", () => {
    const file = photoInput.files?.[0];

    if (!file) {
        localPreview.removeAttribute("src");
        localPreview.classList.remove("is-visible");
        return;
    }

    localPreview.src = URL.createObjectURL(file);
    localPreview.classList.add("is-visible");
});

analysisForm?.addEventListener("submit", () => {
    analysisProgress?.classList.add("is-visible");
});

document.querySelectorAll(".delete-form").forEach((form) => {
    form.addEventListener("submit", (event) => {
        event.preventDefault();
        pendingDeleteForm = form;
        deleteModal?.classList.add("is-visible");
        deleteModal?.setAttribute("aria-hidden", "false");
    });
});

cancelDeleteButton?.addEventListener("click", () => {
    pendingDeleteForm = null;
    deleteModal?.classList.remove("is-visible");
    deleteModal?.setAttribute("aria-hidden", "true");
});

confirmDeleteButton?.addEventListener("click", () => {
    pendingDeleteForm?.submit();
});

deleteModal?.addEventListener("click", (event) => {
    if (event.target === deleteModal) {
        pendingDeleteForm = null;
        deleteModal.classList.remove("is-visible");
        deleteModal.setAttribute("aria-hidden", "true");
    }
});
