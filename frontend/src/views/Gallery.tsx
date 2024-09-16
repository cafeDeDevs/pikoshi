import {
    createSignal,
    createEffect,
    For,
    onMount,
    Show,
    type Component,
} from "solid-js";

import { useNavigate } from "@solidjs/router";
import { useAuthContext } from "../hooks/useAuthContext";
import { useGrabGallery } from "../hooks/useGrabGallery";
import { useModalContext, ModalProvider } from "../contexts/ModalContext";

import urls from "../config/urls";
import Navbar from "../components/Navbar";
import UploadImageModal from "../components/UploadImageModal";
import ImageViewerModal from "../components/ImageViewerModal";

import { delay } from "../utils/utils";
import {
    addThumbnailsToDB,
    getThumbnailsFromDB,
    clearDB,
} from "../utils/indexdb";

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

    // TODO: Wrap in try/catch/throws
    onMount(async () => {
        const authContext = await useAuthContext();
        setIsAuthenticated(authContext);
        if (!isAuthenticated()) {
            await delay(3000);
            return navigate("/");
        }

        const cachedImages = await getThumbnailsFromDB();
        if (cachedImages && cachedImages.length > 0) {
            setImages(cachedImages);
        } else {
            const imagesAsBase64 = await useGrabGallery();
            if (imagesAsBase64) {
                setImages(imagesAsBase64);
                await clearDB();
                await addThumbnailsToDB(imagesAsBase64);
            } else {
                setError(imagesAsBase64);
            }
        }
    });

    // TODO: Wrap in try/catch/throws
    createEffect(async () => {
        if (shouldGalleryReload()) {
            const imagesAsBase64 = await useGrabGallery();
            if (imagesAsBase64) {
                await clearDB();
                await addThumbnailsToDB(imagesAsBase64);
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

    const handleLoadMore = async () => {
        // TODO: set this out as a hook or util function
        try {
            const response = await fetch(
                urls.BACKEND_GALLERY_LOAD_MORE_IMAGES_ROUTE,
                {
                    method: "POST",
                    headers: {
                        Accept: "application/json",
                        "Content-Type": "application/json",
                    },
                    credentials: "include",
                },
            );
            if (!response.ok)
                throw new Error(
                    "An Error Occurred While Trying To Retrieve More Images",
                );
            const jsonRes = await response.json();
            const { imagesAsBase64 } = jsonRes;
            await clearDB();
            const prevImages = images();
            await addThumbnailsToDB([...prevImages, ...imagesAsBase64]);
            setImages([...prevImages, ...imagesAsBase64]);
        } catch (err) {
            const error = err as Error;
            return error.message || "Unknown error";
        }
    };

    return (
        <>
            {/* TODO: Replace Loading... with GalleryLoading component */}
            <Show when={isAuthenticated()} fallback={<p>Loading...</p>}>
                <Navbar />
                <UploadImageModal />
                <ImageViewerModal />
                {/* TODO: Replace button with Intersection Observer scroll event */}
                <button
                    style="background-color: lime;"
                    onClick={handleLoadMore}>
                    Load More Images
                </button>
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
