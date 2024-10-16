import { createEffect, createSignal, Show, type Component } from "solid-js";
import { useModalContext } from "../contexts/ModalContext";

import styles from "../css/UploadImageModal.module.css";

import urls from "../config/urls";

import { compressFiles } from "../utils/utils";

// TODO: Add image previwer in modal
// TODO: compartmentalize out all SVG images
// TODO: Add input fields so that User can title, describe, etc. their image uploads
// i.e. provide meta data for accessibility and file references (make some fields required).
const UploadImageModal: Component = () => {
    const [files, setFiles] = createSignal<File[]>([]);
    const [error, setError] = createSignal<string>("");
    let inputRef: HTMLInputElement | null = null;
    let dropZoneRef: HTMLDivElement | null = null;

    const { isModalOpen, closeModal, reloadGallery } = useModalContext();

    const uploadImage = async (imageData: FormData): Promise<void> => {
        try {
            const response = await fetch(
                urls.BACKEND_GALLERY_UPLOAD_IMAGE_ROUTE,
                {
                    method: "POST",
                    credentials: "include",
                    body: imageData,
                },
            );
            const jsonRes = await response.json();
            if (!response.ok) {
                throw new Error(jsonRes.message || jsonRes.detail);
            }
            reloadGallery(jsonRes.data);
            closeModal();
        } catch (err) {
            const error = err as Error;
            console.error("ERROR :=>", error.message);
            setError(error.message);
        }
    };

    createEffect(async () => {
        if (files().length === 0) return;
        const imageData = await compressFiles(files());
        if (imageData) {
            await uploadImage(imageData);
            setFiles([]);
        } else {
            return setError("Error While Uploading Image.");
        }
    });

    const handleFileChange = (e: Event): void => {
        const target = e.target as HTMLInputElement;
        if (target.files) {
            const file = target.files[0];
            if (!file.type.startsWith("image/")) {
                console.error("ERROR :=> Uploaded file is not an image:", file);
                setError("Please upload a valid image file.");
                return;
            }
            setFiles([...files(), file]);
        }
    };

    const handleDrop = (e: DragEvent): void => {
        e.preventDefault();
        if (dropZoneRef) dropZoneRef.classList.remove(styles.dragover);
        if (e.dataTransfer && e.dataTransfer.files.length > 0) {
            const file = e.dataTransfer.files[0];
            if (!file.type.startsWith("image/")) {
                console.error("ERROR :=> Uploaded file is not an image:", file);
                setError("Please upload a valid image file.");
                return;
            }
            setFiles([...files(), file]);
        }
    };

    const handleDragOver = (e: DragEvent): void => {
        e.preventDefault();
        if (dropZoneRef) dropZoneRef.classList.add(styles.dragover);
    };

    const handleDragLeave = (): void => {
        if (dropZoneRef) dropZoneRef.classList.remove(styles.dragover);
    };

    const handleDropZoneClick = (): void => {
        if (inputRef) inputRef.click();
    };

    return (
        <Show when={isModalOpen()}>
            <div class={styles.ModalOverlay}>
                <div class={styles.UploadImageModal}>
                    <input
                        class={styles["file-picker"]}
                        type="file"
                        accept="image/*"
                        onChange={handleFileChange}
                        ref={el => (inputRef = el)}
                    />
                    <div
                        class={styles["drop-zone"]}
                        onClick={handleDropZoneClick}
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        onDrop={handleDrop}
                        ref={el => (dropZoneRef = el)}>
                        <p>
                            Drag and drop your image here, or click to select
                            image.
                        </p>
                    </div>
                    <button class={styles["close-btn"]} onClick={closeModal}>
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            width="1.03em"
                            height="1.1em"
                            viewBox="0 0 1216 1312">
                            <path
                                fill="currentColor"
                                d="M1202 1066q0 40-28 68l-136 136q-28 28-68 28t-68-28L608 976l-294 294q-28 28-68 28t-68-28L42 1134q-28-28-28-68t28-68l294-294L42 410q-28-28-28-68t28-68l136-136q28-28 68-28t68 28l294 294l294-294q28-28 68-28t68 28l136 136q28 28 28 68t-28 68L880 704l294 294q28 28 28 68"
                            />
                        </svg>
                    </button>
                    <Show when={error().length > 0}>
                        <p style="color: red;">{error()}</p>
                    </Show>
                </div>
            </div>
        </Show>
    );
};

export default UploadImageModal;
