# 🚀 DocAI: Enterprise Document Intelligence Engine

**A highly-available, multi-tenant platform for converting unstructured data streams into structured, queryable knowledge graphs.**

## Status Badges & Tech Stack

| Category | Label | Technology |
| :--- | :--- | :--- |
| **Primary LLM** | [](https://cloud.google.com/gemini) | **Primary LLM** for complex inference, summarization, and zero-shot extraction. |
| **Primary OCR** | [](https://cloud.google.com/vision) | **High-fidelity Cloud OCR** as the default for highest accuracy. |
| **Vector DB** | [](https://www.trychroma.com/) | **Persistent Vector Store** for multi-granular embeddings. |
| **Caching Layer** | [](https://redis.io/) | **Distributed Caching** for high-velocity lookups and cost optimization. |
| **Containerization** | [](https://www.docker.com/) | **Immutable Infrastructure** via containerized service deployment. |
| **API Framework** | [](https://fastapi.tiangolo.com/) | **Asynchronous RESTful API** for low-latency inference. |
| **Fallback LLM** | [](https://ollama.com/) | **Local LLM** for latency-critical tasks and resource-constrained environments. |

-----

## 🎯 Architecture Overview: The Decoupled Pipeline

DocAI operates on a sequential, event-driven architecture, ensuring module independence and scalable processing. The core pipeline is:

$$\text{Document}\xrightarrow{\text{OCR}}\text{Classification}\xrightarrow{\text{Extraction}}\text{Validation}\xrightarrow{\text{Summarization}}\text{Embedding}\xrightarrow{\text{Search}}\text{Export}$$

### 1️⃣ OCR & Text Extraction Module

This module ensures high-fidelity text extraction via a resilient, multi-stage fallback mechanism.

  * **Primary Engine:** **Google Cloud Vision API** (or equivalent **Cloud OCR**) for maximum accuracy and handling of diverse, complex scans.
  * **L1 Fallback:** **PaddleOCR** - Open-source specialization for superior **Table Structure Preservation**.
  * **L2 Fallback:** **Tesseract** - Final, lightweight local fallback for low-complexity documents.
  * **Pre-Processing Filters:** Implementation of image processing kernels for **Noise Reduction (e.g., Median Filter)**, **Adaptive Contrast Enhancement (CLAHE)**, and **Homography-based Deskewing**.

### 2️⃣ Document Classification Module (Hybrid Approach)

Achieves near-perfect categorization by combining deep learning and deterministic logic.

  * **Vector Similarity:** Uses **Sentence Transformers** to embed the OCR output and classify via nearest neighbor search in the ChromaDB knowledge base.
  * **LLM Verification (Gemini):** Primary classification is verified or refined by the **Gemini Pro** model for ambiguity resolution.
  * **Rule Engine:** A deterministic **RegEx/Keyword Rule Engine** provides $100\%$ accuracy for critical document types (e.g., recognizing "Invoice No", "Aadhar Card").

### 3️⃣ Data Extraction & Validation Module

Focuses on structured field extraction and normalization, mitigating LLM hallucination risk via strong validation.

  * **Extraction Engine:** **Gemini Pro** for initial extraction across diverse templates (zero-shot/few-shot).
  * **Post-Extraction Validators:** A suite of dedicated micro-services for normalization:
      * **Financial Validation:** IBAN/BIC/IFSC checksum verification.
      * **Tax Validation:** Country-specific GST/VAT/TIN format validation.
      * **Date Normalization:** Conversion to canonical ISO 8601 format.
  * **Table Reconstruction:** Advanced heuristics for cross-page table stitching and broken row merging.

### 4️⃣ LLM-Powered Modules (Summarization, Auto-Correction)

Leverages the power of **Gemini Pro** for high-level semantic tasks.

  * **Contextual Summarization:** Generates domain-specific summaries (e.g., Financial Risk Summary, Legal Clause Highlight).
  * **Key Insight Extraction:** Prompt-based extraction of **Total Paid**, **Outstanding Balances**, and **Duplicate Document Flags**.
  * **OCR Error Auto-Correction:** The LLM receives OCR snippets (e.g., "Iotal Amourt") with surrounding context and is prompted to apply semantic correction (e.g., to "Total Amount"), enhancing data hygiene.

### 5️⃣ Vector Search & Retrieval (ChromaDB)

The core persistence and query layer, enabling sophisticated $\text{RAG}$-like capabilities over document data.

  * **Multi-Granular Indexing:** Embeddings are stored for: (1) Document $\text{Chunk}$s, (2) Extracted $\text{Fields}$, and (3) $\text{Line Items}$.
  * **Semantic Query Builder:** A $\text{T5}$ or $\text{LLaMA}$ based model converts natural language queries (*"Find invoices above $50,000 from last quarter"*) into structured $\text{SQL/NoSQL/Vector}$ filters.
  * **Duplicate Detection:** High-dimensional vector similarity search across document embeddings for real-time duplicate flagging.

-----

## ⚙️ Engineering & Operational Excellence

### 6️⃣ Caching & Resilience

  * **Redis Caching Layer:** Dedicated, policy-driven caching for: **OCR Results**, **Extraction Results (Full Document Hash)**, and **Vector Embeddings**. This is critical for reducing Cloud OCR/LLM API costs.
  * **Retry Logic:** Exponential backoff and jitter for transient API failures.
  * **Failure Analysis:** Logging of the failure path (e.g., *“OCR failed: Cloud API $\rightarrow$ Fallback $\rightarrow$ FAILED. Reason: Image Resolution too low.”*).

### 7️⃣ Document Comparison

  * **Difference Engine:** Utilizes $\text{Diff}$ algorithms on structured data fields and $\text{semantic chunk}$ing on text to report minute changes between two versions of the same document. **Critical for Contract and Purchase Order tracking.**

### 8️⃣ Export & Serialization

  * **Canonical Outputs:** Exports to standardized $\text{JSON}$ schema, $\text{CSV}$ for tabular data, and $\text{Excel}$ for line items.
  * **Augmented PDF Generation:** Generates a new PDF file with a transparent overlay of the extracted and validated fields, providing visual proof of extraction.

-----
