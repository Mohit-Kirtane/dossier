export const MAX_UPLOAD_SIZE_MB = 5;
export const MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024;

export function checkUploadSize(file) {
  if (file.size > MAX_UPLOAD_SIZE_BYTES) {
    throw new Error(`File is too large. Maximum size is ${MAX_UPLOAD_SIZE_MB} MB.`);
  }
}
