<script lang="ts">
  import axios from 'axios';
  import { writable } from 'svelte/store';
  import { fade } from 'svelte/transition';

  let file: File | null = null;
  let imageUrl: string | null = null;
  let dragOver: boolean = false;
  let copySuccess: boolean = false;
  let error: string | null = null;
  let processing: boolean = false;
  let isModalOpen = false;
  let lineHeight = writable(10);
  let threshold = writable(10);

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
    formData.append('lineHeight', String($lineHeight));
    formData.append('threshold', String($threshold));
    processing = true;

    try {
      const response = await axios.post('http://35.92.136.44/remove_blank_rows/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        responseType: 'blob',
      });

      const blob = new Blob([response.data], { type: 'image/png' });
      imageUrl = URL.createObjectURL(blob);
      copySuccess = false;
      isModalOpen = true;
    } catch (error) {
      console.error('Error uploading file:', error);
    } finally {
      processing = false;
    }
  };

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

  const closeModal = () => {
    isModalOpen = false;
  };
</script>

<main class="h-screen w-screen flex flex-col items-center p-20 bg-white">
  <h1 class="text-3xl font-semibold tracking-tight">Code Squisher</h1>
  <p class="text-neutral-500 mt-2">Remove blank rows from your code screenshots</p>
  <form on:submit|preventDefault={handleSubmit} class="flex flex-col mt-4 w-full max-w-3xl">
    <div 
      class="mt-2 flex flex-col items-center justify-center rounded-lg border border-dashed border-neutral-900/25 px-8 py-20 w-full"
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
          class="relative cursor-pointer rounded-md font-semibold text-indigo-600 focus-within:outline-none focus-within:ring-2 focus-within:ring-indigo-600 focus-within:ring-offset-2 hover:text-indigo-500"
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
    <label class="mt-4">
      <span class="text-sm font-medium">Line Height:</span>
      <input type="number" bind:value={$lineHeight} class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" />
    </label>
    <button 
      type="submit" 
      class="mt-6 px-4 py-2 bg-blue-500 text-white font-semibold rounded-lg shadow-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-opacity-75"
      disabled={processing}
    >
      {processing ? "Processing..." : "Extract Text"}
    </button>
  </form>
  {#if error}
    <p class="text-red-500 mt-4 text-sm font-medium">{error}</p>
  {/if}

  {#if isModalOpen && imageUrl}
    <div class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 transition-opacity">
      <div class="bg-white p-6 rounded-lg shadow-lg w-full max-w-3xl">
        <h2 class="text-xl font-semibold mb-4">Processed Image</h2>
        <img src={imageUrl} alt="Processed Image" class="rounded-lg shadow-md mx-auto" aria-hidden="true" />
        <div class="flex items-center justify-end gap-x-4">
         <button 
          on:click={copyToClipboard} 
          class="text-sm mt-4 px-3.5 py-2.5 bg-green-500 text-white font-semibold rounded-lg shadow-md hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-400 focus:ring-opacity-75"
         disabled={copySuccess}
          >
          {#if copySuccess}
        Image copied to clipboard!
          {:else}
               Copy Image
           {/if}
        </button>
         <button 
          on:click={closeModal} 
          class="text-sm mt-4 px-3.5 py-2.5 bg-red-500 text-white font-semibold rounded-lg shadow-md hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-400 focus:ring-opacity-75"
        >
          Close
        </button>
     
        </div>
      
      
      </div>
    </div>
  {/if}
</main>
