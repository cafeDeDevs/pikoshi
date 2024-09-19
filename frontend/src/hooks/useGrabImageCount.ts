const useGrabImageCount = async (): Promise<number> => {
    try {
        const response = await fetch(
            "http://localhost:8000/gallery/image-count/",
            {
                method: "POST",
                headers: {
                    Accept: "application/json",
                    "Content-Type": "application/json",
                },
                credentials: "include",
            },
        );
        if (response.status === 204) {
            console.warn("WARNING :=> No More Images Available in Album");
            return 0;
        }
        const { image_count } = await response.json();
        return image_count;
    } catch (err) {
        const error = err as Error;
        console.error("ERROR :=>", error.message);
        return 0;
    }
};

export { useGrabImageCount };
