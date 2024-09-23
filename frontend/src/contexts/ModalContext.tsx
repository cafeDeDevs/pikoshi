import { createSignal, createContext, useContext } from "solid-js";
import type { Accessor, JSX } from "solid-js";

interface ImageMetadata {
    data: string; // Base64 encoded image data
    type: string; // Metadata field, e.g. "original", "mobile"
    file_name: string; // Name of File
}

type ModalContextType = {
    isModalOpen: Accessor<boolean>;
    isImageModalOpen: Accessor<boolean>;
    isLogoutModalOpen: Accessor<boolean>;
    newImageData: Accessor<ImageMetadata>;
    shouldGalleryReload: Accessor<boolean>;
    selectedImage: Accessor<ImageMetadata | null>;
    openModal: () => void;
    openImageModal: (image: ImageMetadata | null) => void;
    openLogoutModal: () => void;
    closeModal: () => void;
    closeImageModal: () => void;
    closeLogoutModal: () => void;
    reloadGallery: (image?: ImageMetadata | undefined) => void;
};

const ModalContext = createContext<ModalContextType>();

export const ModalProvider = (props: {
    children: JSX.Element;
}): JSX.Element => {
    const [isModalOpen, setIsModalOpen] = createSignal(false);
    const [newImageData, setNewImageData] = createSignal<ImageMetadata>({
        data: "",
        type: "",
        file_name: "",
    });
    const [isImageModalOpen, setIsImageModalOpen] = createSignal(false);
    const [isLogoutModalOpen, setIsLogoutModalOpen] = createSignal(false);
    const [shouldGalleryReload, setShouldGalleryReload] = createSignal(false);
    const [selectedImage, setSelectedImage] =
        createSignal<ImageMetadata | null>(null);

    const openModal = () => setIsModalOpen(true);
    const closeModal = () => setIsModalOpen(false);
    const reloadGallery = (image?: ImageMetadata) => {
        if (image) setNewImageData(image);
        setShouldGalleryReload(!shouldGalleryReload());
    };

    const openImageModal = (image: ImageMetadata | null) => {
        setSelectedImage(image);
        setIsImageModalOpen(true);
    };

    const closeImageModal = () => {
        setSelectedImage(null);
        setIsImageModalOpen(false);
    };

    const openLogoutModal = () => {
        setIsLogoutModalOpen(true);
    };

    const closeLogoutModal = () => {
        setIsLogoutModalOpen(false);
    };

    const value = {
        isModalOpen: isModalOpen,
        isImageModalOpen: isImageModalOpen,
        isLogoutModalOpen: isLogoutModalOpen,
        newImageData: newImageData,
        shouldGalleryReload: shouldGalleryReload,
        selectedImage: selectedImage,
        openModal,
        openImageModal,
        openLogoutModal,
        closeModal,
        closeImageModal,
        closeLogoutModal,
        reloadGallery,
    };

    return (
        <ModalContext.Provider value={value}>
            {props.children}
        </ModalContext.Provider>
    );
};

export const useModalContext = () => {
    const context = useContext(ModalContext);
    if (!context) {
        throw new Error("useModalContext must be used within a ModalProvider");
    }
    return context;
};
