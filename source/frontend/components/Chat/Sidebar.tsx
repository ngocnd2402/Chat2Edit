import React, { FC, useState, useRef } from 'react';
import Link from 'next/link';
import { ImageInfo } from "@/utils/types";
import MediaModal  from '@/components/Chat/MediaModal';

interface SidebarProps {
    onImagesUploaded: (images: ImageInfo[]) => void;
    onKeepTrackChange?: (keepTrack: boolean) => void;
}

const Sidebar: FC<SidebarProps> = ({ onImagesUploaded, onKeepTrackChange }) => {
    const [images, setImages] = useState<ImageInfo[]>([]);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [keepTrack, setKeepTrack] = useState<boolean>(false);
    const [showModal, setShowModal] = useState<boolean>(false);
    const [modalSrc, setModalSrc] = useState<string | null>(null);

    const handleImagesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            const files = Array.from(e.target.files);
            Promise.all(files.map((file, index) => {
                return new Promise<ImageInfo>((resolve, reject) => {
                    const reader = new FileReader();
                    reader.onloadend = () => {
                        resolve({ index, base64_string: reader.result as string });
                    };
                    reader.onerror = reject;
                    reader.readAsDataURL(file);
                });
            }))
            .then(newImages => {
                const updatedImages = [...images, ...newImages];
                setImages(updatedImages);
                onImagesUploaded(updatedImages);
            })
            .catch(error => console.error("Error uploading files: ", error));
            e.target.value = '';
        }
    };
    

    const removeImage = (imageId: number) => {
        const updatedImages = images.filter(image => image.index !== imageId);
        setImages(updatedImages);
        onImagesUploaded(updatedImages);
    };

    const triggerFileInputClick = () => fileInputRef.current?.click();

    const handleKeepTrackChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setKeepTrack(e.target.checked);
        onKeepTrackChange?.(e.target.checked);
        console.log('keepTrack:', e.target.checked);
    };

    const openModal = (src: string): void => {
        setModalSrc(src);
        setShowModal(true);
    };

    const closeModal = (): void => {
        setShowModal(false);
        setModalSrc(null);
    };

    return (
        <>
            <aside className='w-[512px] border-gray-300 border-r-[0.5px] bg-white py-6 px-8 flex flex-col justify-between'>
                <div>
                    <Link href="/">
                        <button className={`font-black uppercase text-lg mb-4`}>
                            <svg height="28" viewBox="0 0 135 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M10.12 32L0.552 9.6H7.4L15.464 28.992H11.432L19.688 9.6H25.96L16.36 32H10.12ZM31.1113 32V9.6H37.4473V32H31.1113ZM51.619 18.272H62.019V23.008H51.619V18.272ZM52.067 27.104H63.779V32H45.795V9.6H63.363V14.496H52.067V27.104ZM71.135 32V9.6H81.727C84.2017 9.6 86.3777 10.0587 88.255 10.976C90.1323 11.8933 91.5937 13.184 92.639 14.848C93.7057 16.512 94.239 18.496 94.239 20.8C94.239 23.0827 93.7057 25.0667 92.639 26.752C91.5937 28.416 90.1323 29.7067 88.255 30.624C86.3777 31.5413 84.2017 32 81.727 32H71.135ZM77.471 26.944H81.471C82.751 26.944 83.8603 26.7093 84.799 26.24C85.759 25.7493 86.5057 25.0453 87.039 24.128C87.5723 23.1893 87.839 22.08 87.839 20.8C87.839 19.4987 87.5723 18.3893 87.039 17.472C86.5057 16.5547 85.759 15.8613 84.799 15.392C83.8603 14.9013 82.751 14.656 81.471 14.656H77.471V26.944ZM101.413 32V9.6H107.749V32H101.413ZM120.864 32V14.624H113.984V9.6H134.048V14.624H127.2V32H120.864Z" fill="#020008" />
                                <circle cx="34.5" cy="3.5" r="3.5" fill="#020008" />
                                <circle cx="104.5" cy="3.5" r="3.5" fill="#020008" />
                            </svg>

                        </button>
                    </Link>
                    <h2 className="text-lg font-semibold text-black my-4">Upload Images</h2>
                    {images.length === 0 ? (
                        <div className="flex flex-col gap-4 items-center justify-center w-full">
                            <div className="flex flex-col items-center justify-center h-fit p-8 rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100 w-full">
                                <div className="flex flex-col items-center justify-center">
                                    <svg className="w-8 h-8 mb-4 text-gray-500 dark:text-gray-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 16">
                                        <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2" />
                                    </svg>
                                    <p className="mb-2 text-sm text-gray-500 dark:text-gray-400"><span className="font-semibold">Click to upload</span> or drag and drop</p>
                                    <p className="text-xs text-gray-500 dark:text-gray-400">SVG, PNG, JPG or GIF</p>
                                </div>
                                <input ref={fileInputRef} id="dropzone-file" type="file" multiple className="hidden" onChange={handleImagesChange} />
                                <button onClick={triggerFileInputClick} className='px-4 py-2 mt-4 text-sm bg-primary rounded-full font-medium text-white hover:bg-black hover:text-primary'>Upload Images</button>
                            </div>
                            <div id="empty" className="h-full w-full text-center flex flex-col justify-center items-center">
                                <img className="mx-auto w-32" src="https://user-images.githubusercontent.com/507615/54591670-ac0a0180-4a65-11e9-846c-e55ffce0fe7b.png" alt="no data" />
                                <span className="text-small text-gray-500">No files selected</span>
                            </div>
                        </div>
                    ) : (
                        <div className="grid grid-cols-2 gap-2">
                            {images.map((image) => (
                                <div key={image.index} className="relative">
                                    <img src={image.base64_string} alt={`uploaded-img-${image.index}`} className="object-cover rounded-md w-full h-28 cursor-pointer" onClick={() => openModal(image.base64_string)}/>
                                    <div className="absolute top-0 right-0 text-primary rounded-full px-1.5 py-0">
                                        <button aria-label="Remove" className='fill-primary' onClick={() => removeImage(image.index)}>
                                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                                <path d="M6.34315 6.34338L17.6569 17.6571M17.6569 6.34338L6.34315 17.6571" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"></path>
                                            </svg>
                                        </button>
                                    </div>
                                </div>
                            ))}
                            <div>
                                <input ref={fileInputRef} id="dropzone-file" type="file" multiple className="hidden" onChange={handleImagesChange} />
                                <button className="cursor-pointer p-4 border-2 border-dashed border-gray-300 rounded-md flex flex-col justify-center items-center w-full text-sm h-28" onClick={triggerFileInputClick}>
                                    <svg width="64px" height="64px" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M31.5,24.5h-15a0.5,0.5,0,0,1,0-1h15A0.5,0.5,0,0,1,31.5,24.5Z" />
                                        <path d="M24,32a0.5,0.5,0,0,1-.5-0.5v-15a0.5,0.5,0,0,1,1,0v15A0.5,0.5,0,0,1,24,32Z" />
                                        <rect width="48" height="48" fill="none" />
                                    </svg>
                                    <span>Add more</span>
                                </button>
                            </div>
                        </div>
                    )}
                    {showModal && <MediaModal isOpen={showModal} onClose={closeModal} src={modalSrc} />}
                </div>
                <div className="mb-4">
                    <label htmlFor="keepTrack" className="flex items-center gap-2 cursor-pointer">
                        <input
                            id="keepTrack"
                            type="checkbox"
                            checked={keepTrack}
                            onChange={handleKeepTrackChange}
                            className="accent-primary w-4 h-4 rounded-sm"
                        />
                        Keep track of edits
                    </label>
                </div>
            </aside>
        </>
    )
}

export default Sidebar;