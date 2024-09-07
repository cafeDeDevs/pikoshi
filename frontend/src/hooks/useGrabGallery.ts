import urls from "../config/urls";

const useGrabGallery = async (): Promise<any> => {
    try {
        const windowWidth = window.innerWidth;

        const response = await fetch(urls.BACKEND_GALLERY_INITIAL_ROUTE, {
            method: "POST",
            headers: {
                Accept: "application/json",
                "Content-Type": "application/json",
            },
            credentials: "include",
            body: JSON.stringify({ width: windowWidth }),
        });
        const jsonRes = await response.json();

        if (!response.ok)
            throw new Error(
                "An Error Occurred While Trying To Retrieve Your Gallery",
            );

        const { imagesAsBase64 } = jsonRes;
        // setImages(imagesAsBase64);
        if (imagesAsBase64) return imagesAsBase64;
    } catch (err) {
        const error = err as Error;
        return error.message || "Unknown error";
    }
};

export { useGrabGallery };
