import { Show, type Component } from "solid-js";
import { useModalContext } from "../contexts/ModalContext";

import styles from "../css/ImageViewerModal.module.css";

const ImageViewerModal: Component = () => {
    const { isImageModalOpen, selectedImage, closeImageModal } =
        useModalContext();
    return (
        <Show when={isImageModalOpen()}>
            <div class={styles.ModalOverlay} onClick={closeImageModal}>
                <div
                    class={styles.ImageViewerModal}
                    onclick={e => e.stopPropagation()}>
                    {/* TODO: set alt tag to user defined alt */}
                    <img
                        src={`data:image/webp;base64,${selectedImage()?.data}`}
                        alt="Selected Image"
                        class={styles["image-viewer"]}
                    />
                </div>
            </div>
        </Show>
    );
};

export default ImageViewerModal;
