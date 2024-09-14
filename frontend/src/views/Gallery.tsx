import {
    createSignal,
    createEffect,
    For,
    Show,
    type Component,
} from "solid-js";

import { useNavigate } from "@solidjs/router";
import { useAuthContext } from "../hooks/useAuthContext";
import { useGrabGallery } from "../hooks/useGrabGallery";
import { useModalContext, ModalProvider } from "../contexts/ModalContext";

import Navbar from "../components/Navbar";
import UploadImageModal from "../components/UploadImageModal";
import ImageViewerModal from "../components/ImageViewerModal";

import { delay } from "../utils/utils";

import styles from "../css/Gallery.module.css";

interface ImageMetadata {
    data: string; // Base64 encoded image data
    type: string; // Metadata field, e.g. "original", "mobile"
    file_name: string; // Name of File
}

// TODO: Figure out how to pass optional params (i.e. gallery/default)
// And Then pass this param "default" as an album_name to the backend
const Gallery: Component = () => {
    const [isAuthenticated, setIsAuthenticated] = createSignal<boolean>(false);
    const [error, setError] = createSignal<string>("");
    const [images, setImages] = createSignal<ImageMetadata[]>([]);
    const { openImageModal, reloadGallery, shouldGalleryReload } =
        useModalContext();

    const navigate = useNavigate();

    createEffect(async () => {
        const authContext = await useAuthContext();
        setIsAuthenticated(authContext);
        if (!isAuthenticated()) {
            await delay(3000);
            return navigate("/");
        }
        const imagesAsBase64 = await useGrabGallery();
        if (imagesAsBase64) {
            setImages(imagesAsBase64);
        } else {
            setError(imagesAsBase64);
        }
    });

    createEffect(async () => {
        if (shouldGalleryReload()) {
            const imagesAsBase64 = await useGrabGallery();
            if (imagesAsBase64) {
                setImages(imagesAsBase64);
            } else {
                setError(imagesAsBase64);
            }
            reloadGallery();
        }
    });

    const handleImgClick = (index: number) => {
        const image = images()[index];
        openImageModal(image);
    };

    return (
        <>
            {/* TODO: Replace Loading... with GalleryLoading component */}
            <Show when={isAuthenticated()} fallback={<p>Loading...</p>}>
                <Navbar />
                <UploadImageModal />
                <ImageViewerModal />
                <div class={styles.Gallery}>
                    {/* TODO: Replace Loading... with ImageLoading Component */}
                    <Show
                        when={images().length > 0}
                        fallback={<p>Loading...</p>}>
                        <div class={styles["gallery"]}>
                            <For each={images()}>
                                {(image, index) => (
                                    <img
                                        src={`data:image/webp;base64,${image.data}`}
                                        alt={`Gallery Image ${index() + 1}`}
                                        data-name={image.file_name}
                                        onClick={() => handleImgClick(index())}
                                    />
                                )}
                            </For>
                        </div>
                    </Show>
                    <Show when={error().length > 0}>
                        <p style="color: red;">{error()}</p>
                    </Show>
                </div>
            </Show>
        </>
    );
};

const GalleryWrapper: Component = () => {
    return (
        <ModalProvider>
            <Gallery />
        </ModalProvider>
    );
};

export default GalleryWrapper;
