import urls from "../config/urls";

interface ImageMetadata {
    data: string; // Base64 encoded image data
    type: string; // Metadata field, e.g. "original", "mobile"
    file_name: string; // Name of File
}

const useStreamGallery = async function* (
    url: string,
    abortController: AbortController,
) {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
        },
        credentials: "include",
        signal: abortController.signal,
    });

    const reader = response.body!.getReader();
    const boundary = response.headers.get("X-Boundary");
    const decoder = new TextDecoder();
    let done = false;
    let base64Chunk = "";

    while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (value) {
            base64Chunk += decoder.decode(value, { stream: true });
            const parts = base64Chunk.split(`${boundary}`).filter(Boolean);

            for (const part of parts) {
                const contentDispositionMatch = part.match(
                    /Content-Disposition: form-data; name="file"; filename="(.+)"/,
                );
                const contentTypeMatch = part.match(/Content-Type: (.+)/);
                const base64DataMatch = part.match(/\r\n\r\n([\s\S]+?)\r\n/);

                if (
                    contentDispositionMatch &&
                    contentTypeMatch &&
                    base64DataMatch
                ) {
                    const fileName = contentDispositionMatch[1];
                    const fileType = contentTypeMatch[1];
                    const base64Data = base64DataMatch[1];

                    const imageMetaData: ImageMetadata = {
                        data: base64Data,
                        type: fileType,
                        file_name: fileName,
                    };
                    yield imageMetaData;
                }
            }
        }
        base64Chunk = "";
    }
};

export { useStreamGallery };
