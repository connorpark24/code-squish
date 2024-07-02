<script lang="ts">
  import axios from 'axios';
  let file: File | null = null;
  let imageUrl: string | null = null;
  let dragOver: boolean = false;
  let copySuccess: boolean = false;
  let error: string | null = null
  
  const copyToClipboard = async (): Promise<void> => {
    if (!imageUrl) return;

    try {
      const img = await fetch(imageUrl);
      const imgBlob = await img.blob();
      await navigator.clipboard.write([
        new ClipboardItem({
          'image/png': imgBlob,
        }),
      ]);
      copySuccess = true;
    } catch (error) {
      console.error('Failed to copy image to clipboard:', error);
      copySuccess = false;
    }
  };
  const handleFileChange = (e: Event): void => {
    const input = e.target as HTMLInputElement;
    if (input.files) {
      file = input.files[0];
      error = null;
    }
  };

  const handleDragOver = (e: DragEvent) => {
    e.preventDefault();
    dragOver = true;
  };

  const handleDragLeave = (e: DragEvent) => {
    e.preventDefault();
    dragOver = false;
  };

  const handleDrop = (e: DragEvent) => {
    e.preventDefault();
    dragOver = false;
    const files = e.dataTransfer?.files;
    if (files) {
      file = files[0];
      error = null;
    }
  };

  const handleSubmit = async (e: Event): Promise<void> => {
    e.preventDefault();
    if (!file) {
      error = 'Please upload a file';
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/remove_blank_rows/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        responseType: 'blob', 
      });

      const blob = new Blob([response.data], { type: 'image/png' });
      imageUrl = URL.createObjectURL(blob);
      console.log('Image URL:', imageUrl);
      copySuccess = false;
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };
</script>

<main class="h-screen w-screen flex bg-neutral-50">
  <div class="max-w-4xl mx-auto my-auto flex flex-col items-center p-8 bg-white shadow-lg rounded-lg">
    <h1 class="text-3xl font-semibold tracking-tight">Code Squisher</h1>
    <form on:submit|preventDefault={handleSubmit} class="w-full flex flex-col items-center mt-2">
      <div 
        class="mt-2 flex flex-col items-center justify-center rounded-lg border border-dashed border-neutral-900/25 px-32 py-20"
        on:dragover={handleDragOver}
        on:dragleave={handleDragLeave}
        on:drop={handleDrop}
        aria-label="File Upload"
        role="button"
        tabindex="0"
        class:bg-neutral-200={dragOver}
      >
        <input 
          id="file-upload" 
          name="file-upload" 
          type="file" 
          class="sr-only" 
          on:change={handleFileChange} 
        />
        <div class="mt-4 flex text-sm leading-6 text-neutral-600">
          <label
            for="file-upload"
            class="relative cursor-pointer rounded-md bg-white font-semibold text-indigo-600 focus-within:outline-none focus-within:ring-2 focus-within:ring-indigo-600 focus-within:ring-offset-2 hover:text-indigo-500"
          >
            <span>Upload a file</span>
          </label>
          <p class="pl-1">or drag and drop</p>
        </div>
        <p class="text-xs leading-5 text-neutral-600">PNG, JPG, GIF up to 10MB</p>
        {#if file}
          <p class="text-sm text-neutral-500 mt-2">{file.name}</p>
        {/if}
      </div>
      <button 
        type="submit" 
        class="text-sm mt-4 px-4 py-2 bg-blue-500 text-white font-semibold rounded-lg shadow-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-opacity-75"
      >
        Extract Text
      </button>
    </form>
    {#if error}
      <p class="text-red-500 mt-4 text-sm font-medium">{error}</p>
    {/if}
    {#if imageUrl}
      <div class="mt-6 w-full">
        <h2 class="text-xl font-semibold mb-2">Processed Image:</h2>
        <img src={imageUrl} alt="processed" class="w-full  shadow-md" />
        <button 
          on:click={copyToClipboard} 
          class="mt-4 px-4 py-2 bg-green-500 text-white font-semibold rounded-lg shadow-md hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-400 focus:ring-opacity-75"
        >
          Copy Image URL
        </button>
        {#if copySuccess}
          <p class="text-green-500 mt-2">Image URL copied to clipboard!</p>
        {/if}
      </div>
    {/if}
  </div>
</main>