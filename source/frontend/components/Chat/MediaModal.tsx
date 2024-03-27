import React from 'react';
import { MediaModalProps } from '@/utils/types';

const MediaModal: React.FC<MediaModalProps> = ({ isOpen, onClose, src }) => {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50 bg-black/90 backdrop-blur-xl radix-state-open:animate-show pointer-events-auto">
            <div className="relative flex h-[100dvh] w-screen justify-stretch divide-x divide-white/10 focus:outline-none pointer-events-auto" tabIndex={-1}>
                <div className="flex flex-1 transition-[flex-basis] md:basis-[75vw]">
                    <div className="flex flex-1 flex-col md:p-6">
                        <div className="flex justify-between px-6 py-2 pt-6 text-white sm:mb-4 md:mt-2 md:px-0 md:py-2">
                            <button className="btn relative btn-small" aria-label="Download Image">
                                <div className="flex w-full gap-2 items-center justify-center">
                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path fill-rule="evenodd" clip-rule="evenodd" d="M7.70711 10.2929C7.31658 9.90237 6.68342 9.90237 6.29289 10.2929C5.90237 10.6834 5.90237 11.3166 6.29289 11.7071L11.2929 16.7071C11.6834 17.0976 12.3166 17.0976 12.7071 16.7071L17.7071 11.7071C18.0976 11.3166 18.0976 10.6834 17.7071 10.2929C17.3166 9.90237 16.6834 9.90237 16.2929 10.2929L13 13.5858L13 4C13 3.44771 12.5523 3 12 3C11.4477 3 11 3.44771 11 4L11 13.5858L7.70711 10.2929ZM5 19C4.44772 19 4 19.4477 4 20C4 20.5523 4.44772 21 5 21H19C19.5523 21 20 20.5523 20 20C20 19.4477 19.5523 19 19 19L5 19Z" fill="currentColor"></path>
                                    </svg>
                                </div>
                            </button>
                            <button aria-label="Close Modal" onClick={onClose}>
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M6.34315 6.34338L17.6569 17.6571M17.6569 6.34338L6.34315 17.6571" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path>
                                </svg>
                            </button>
                        </div>
                        <div className="relative flex flex-1 flex-col items-center justify-center overflow-hidden">
                            <div className="absolute grid h-full w-full grid-rows-2 select-none touch-pan-y transform-none" draggable="false">
                                {
                                    src && src.startsWith('data:image') && <img src={src} alt="Modal Content" className="row-span-4 mx-auto h-full object-scale-down" />
                                }
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MediaModal;