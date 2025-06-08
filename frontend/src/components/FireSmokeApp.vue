<template>
  <div class="app-container container-mobile safe-area-top safe-area-bottom">
    <h1 class="heading-responsive no-select">Fire Smoke Web App <span class="emoji">🔥</span></h1>
    <p class="text-responsive">This is a simple web application to demonstrate fire-smoke-detection</p>
    <p class="text-responsive">Credits to the creator: Sayed Gamal</p>
    <a
      href="https://github.com/sayedgamal99/Real-Time-Smoke-Fire-Detection-YOLO11"
      target="_blank"
      rel="noopener"
      class="text-responsive"
    >
      https://github.com/sayedgamal99/Real-Time-Smoke-Fire-Detection-YOLO11
    </a>

    <CurrentTime />

    <div class="button spacing-responsive">
      <button @click="openModal" class="touch-target">Click to run Live Camera</button>
    </div>

    <CameraModal :isVisible="isModalVisible" @close="closeModal" />
  </div>
</template>

<script>
import { ref } from "vue";
import CurrentTime from "./CurrentTime.vue";
import CameraModal from "./CameraModal.vue";

export default {
  name: "FireSmokeApp",
  components: {
    CurrentTime,
    CameraModal,
  },
  setup() {
    const isModalVisible = ref(false);

    const openModal = () => {
      isModalVisible.value = true;
    };

    const closeModal = () => {
      isModalVisible.value = false;
    };

    return {
      isModalVisible,
      openModal,
      closeModal,
    };
  },
};
</script>

<style scoped>
/* Component-specific mobile optimizations */
.app-container {
  padding: 1rem;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

@media (max-width: 768px) {
  .app-container {
    padding: 0.5rem;
    min-height: 90vh;
  }
}

@media (max-width: 480px) {
  .app-container {
    padding: 0.25rem;
  }
}
</style>
