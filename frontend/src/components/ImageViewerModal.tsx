import { createEffect, createSignal, Show, type Component } from "solid-js";
import { useModalContext } from "../contexts/ModalContext";

import styles from "../css/ImageViewerModal.module.css";
import urls from "../config/urls";

interface ImageMetadata {
    data?: string; // Base64 encoded image data
    type?: string; // Metadata field, e.g. "original", "mobile"
    file_name?: string; // Name of File
}

const ImageViewerModal: Component = () => {
    const [image, setImage] = createSignal<ImageMetadata>({});
    const { isImageModalOpen, selectedImage, closeImageModal } =
        useModalContext();

    createEffect(async () => {
        const fileName = selectedImage()?.file_name;
        if (!fileName) return;
        // TODO: Check if image is in Cache (index db??)
        // If it is, then just set the image to the cached image and return
        // Otherwise, continue
        setImage({});
        const windowWidth = window.innerWidth;

        const response = await fetch(
            urls.BACKEND_GALLERY_GRAB_SINGLE_IMAGE_ROUTE,
            {
                method: "POST",
                headers: {
                    Accept: "application/json",
                    "Content-Type": "application/json",
                },
                credentials: "include",
                body: JSON.stringify({
                    width: windowWidth,
                    file_name: fileName,
                }),
            },
        );
        const jsonRes = await response.json();
        if (!response.ok)
            console.warn("An Error Occurred While Trying To Retrieve Image");
        console.log("jsonRes :=>", jsonRes);
        setImage(jsonRes.imageAsBase64);
    });

    return (
        <Show when={isImageModalOpen()}>
            <div class={styles.ModalOverlay} onClick={closeImageModal}>
                <div
                    class={styles.ImageViewerModal}
                    onclick={e => e.stopPropagation()}>
                    <button
                        class={styles["close-btn"]}
                        onClick={closeImageModal}>
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
                    {/* TODO: set alt tag to user defined alt */}
                    <Show
                        when={image()?.data?.length}
                        fallback={<p>Loading...</p>}>
                        <img
                            src={`data:image/webp;base64,${image()?.data}`}
                            alt="Selected Image"
                            data-name={image()?.file_name}
                            class={styles["image-viewer"]}
                        />
                    </Show>
                </div>
            </div>
        </Show>
    );
};

export default ImageViewerModal;
