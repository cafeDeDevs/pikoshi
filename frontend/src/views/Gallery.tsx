import {
    createSignal,
    createEffect,
    For,
    onCleanup,
    onMount,
    Show,
    type Component,
} from "solid-js";

import urls from "../config/urls";

import { useNavigate } from "@solidjs/router";
import { useAuthContext } from "../hooks/useAuthContext";
import { useStreamGallery } from "../hooks/useStreamGallery";
import { useGrabImageCount } from "../hooks/useGrabImageCount";
import { useModalContext, ModalProvider } from "../contexts/ModalContext";

import Navbar from "../components/Navbar";
import UploadImageModal from "../components/UploadImageModal";
import ImageViewerModal from "../components/ImageViewerModal";
import LogoutSuccessModal from "../components/LogoutSuccessModal";

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

// TODO: Address BUG:
// BUG: On Refresh Images are out of order
// (cache ordering is different than backend load ordering)
const Gallery: Component = () => {
    const [isAuthenticated, setIsAuthenticated] = createSignal<boolean>(false);
    const [error, setError] = createSignal<string>("");
    const [images, setImages] = createSignal<ImageMetadata[]>([]);
    const [loadingStates, setLoadingStates] = createSignal<boolean[]>([]);
    const [imagesLoaded, setImagesLoaded] = createSignal<boolean>(false);
    const [isScrollingDown, setIsScrollingDown] = createSignal<boolean>(false);

    const [observerRef, setObserverRef] = createSignal<HTMLDivElement>();
    const [lastScrollY, setLastScrollY] = createSignal<number>(0);

    const {
        openImageModal,
        isLogoutModalOpen,
        closeLogoutModal,
        reloadGallery,
        newImageData,
        shouldGalleryReload,
    } = useModalContext();

    const navigate = useNavigate();

    const abortController = new AbortController();

    // TODO: Wrap in try/catch/throws
    onMount(async () => {
        const authContext = await useAuthContext();
        setIsAuthenticated(authContext);
        if (!isAuthenticated()) {
            await delay(3000);
            return navigate("/");
        }

        window.addEventListener("scroll", handleScroll);

        if (isLogoutModalOpen()) closeLogoutModal();

        const cachedImages = await getThumbnailsFromDB();
        if (cachedImages && cachedImages.length > 0) {
            setImages(cachedImages);
            setImagesLoaded(true);
        } else {
            const imageCount = await useGrabImageCount();
            if (imageCount) {
                setLoadingStates(Array(imageCount).fill(true));

                const streamGallery = useStreamGallery(
                    urls.BACKEND_GALLERY_INITIAL_ROUTE,
                    abortController,
                );

                for await (const imageMetaData of streamGallery) {
                    setImages(prev => [...prev, imageMetaData]);
                    setLoadingStates(prev => {
                        const newState = [...prev];
                        newState.shift();
                        return newState;
                    });
                }
                await addThumbnailsToDB(images());
                setImagesLoaded(true);
            }
        }
    });

    createEffect(async () => {
        if (shouldGalleryReload()) {
            const newImage = newImageData();
            setImages(prev => [newImage, ...prev]);
            const cachedImages = await getThumbnailsFromDB();
            await clearDB();
            await addThumbnailsToDB([newImage, ...cachedImages]);
            reloadGallery();
        }
    });

    createEffect(() => {
        if (!imagesLoaded() || !isScrollingDown()) return;

        const observerOptions = {
            root: null,
            rootMargin: "-250px",
            threshold: 0,
        };

        const observerCallBack = (entries: IntersectionObserverEntry[]) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    handleLoadMore();
                }
            });
        };

        const observer = new IntersectionObserver(
            observerCallBack,
            observerOptions,
        );

        if (observerRef) observer.observe(observerRef()!);

        onCleanup(() => {
            if (observerRef) observer.unobserve(observerRef()!);
        });
    });

    const handleScroll = () => {
        if (window.scrollY > lastScrollY()) {
            setLastScrollY(window.scrollY);
            setIsScrollingDown(true);
        } else {
            setLastScrollY(window.scrollY - 1);
            setIsScrollingDown(false);
        }
    };

    const handleImgClick = (index: number) => {
        const image = images()[index];
        openImageModal(image);
    };

    const handleLoadMore = async () => {
        try {
            setImagesLoaded(false);
            const imageCount = await useGrabImageCount();
            setLoadingStates(Array(imageCount).fill(true));

            const streamMoreGallery = useStreamGallery(
                urls.BACKEND_GALLERY_LOAD_MORE_IMAGES_ROUTE,
                abortController,
            );

            for await (const imageMetaData of streamMoreGallery) {
                setImages(prev => [...prev, imageMetaData]);
                setLoadingStates(prev => {
                    const newState = [...prev];
                    newState.shift();
                    return newState;
                });
            }
            await clearDB();
            await addThumbnailsToDB(images());
            setImagesLoaded(true);
        } catch (err) {
            const error = err as Error;
            console.error("ERROR :=>", error.message);
            setError(error.message);
        }
    };

    onCleanup(() => {
        abortController.abort();
        window.removeEventListener("scroll", handleScroll);
    });

    return (
        <>
            {/* TODO: Replace Loading... with GalleryLoading component */}
            <Show when={isAuthenticated()} fallback={<p>Loading...</p>}>
                <Navbar />
                <UploadImageModal />
                <ImageViewerModal />
                <LogoutSuccessModal />
                <div class={styles.Gallery}>
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
                                        data-type={image.type}
                                        onClick={() => handleImgClick(index())}
                                        loading="lazy"
                                        decoding="async"
                                    />
                                )}
                            </For>
                            <For each={loadingStates()}>
                                {(_, index) => (
                                    <Show when={loadingStates()[index()]}>
                                        <div class={styles["spinner"]}>
                                            <div></div>
                                            <div></div>
                                            <div></div>
                                            <div></div>
                                        </div>
                                    </Show>
                                )}
                            </For>
                        </div>
                    </Show>
                    <Show when={imagesLoaded()}>
                        <div ref={setObserverRef}></div>
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
