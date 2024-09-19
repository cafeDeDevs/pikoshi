const useGrabImageCount = async () => {
    const response = await fetch("http://localhost:8000/gallery/image-count/", {
        method: "POST",
        headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
        },
        credentials: "include",
    });
    const { image_count } = await response.json();
    return image_count;
};

export { useGrabImageCount };
