import express from "express";
import bodyParser from "body-parser";
import multer from "multer";
import ffmpeg from "fluent-ffmpeg";
import path from "path";
import fs from "fs";
import axios from "axios";
import FormData from "form-data";

const app = express();
const port = 3000;

app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, "uploads/");
  },
  filename: (req, file, cb) => {
    cb(null, Date.now() + path.extname(file.originalname));
  },
});

const upload = multer({ storage });

app.use("/uploads", express.static("uploads"));

app.get("", (req, res) => {
  res.render("index.ejs", { Path: null });
});

app.post("/upload", upload.single("video"), async (req, res) => {
  try {
    const videoPath = req.file.path;

    const formData = new FormData();
    formData.append("video", fs.createReadStream(videoPath));

    const externalServiceUrl = "http://127.0.0.1:5000/process-video";

    const response = await axios.post(externalServiceUrl, formData, {
      headers: {
        ...formData.getHeaders(),
      },
    });

    const { timestamps } = response.data;

    const gifs = [];

    for (const { start, end, caption } of timestamps) {
      const gifPath = `uploads/output-${Date.now()}-${caption.replace(/\s+/g, "_")}.gif`;
      gifs.push(gifPath);

      await new Promise((resolve, reject) => {
        ffmpeg(videoPath)
          .setStartTime(start)
          .setDuration(end - start)
          .output(gifPath)
          .on("end", resolve)
          .on("error", reject)
          .run();
      });
    }

    res.render("index.ejs", { Path: gifs });
  } catch (error) {
    console.error("Error processing the video:", error);
    res.status(500).send("Error processing the video");
  }
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
