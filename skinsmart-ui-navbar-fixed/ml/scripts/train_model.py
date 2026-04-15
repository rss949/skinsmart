import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint

IMG_SIZE = 224
BATCH_SIZE = 16
EPOCHS = 30
VAL_SPLIT = 0.2
SEED = 42

TRAIN_DIR = "ml/dataset/train"
TEST_DIR = "ml/dataset/test"
BEST_MODEL_PATH = "ml/model/best_model.h5"
FINAL_MODEL_PATH = "ml/model/skin_model.h5"


def _class_weights_from_generator(generator):
    counts = np.bincount(generator.classes)
    total = np.sum(counts)
    num_classes = len(counts)
    # Inverse-frequency balancing.
    return {i: float(total) / (num_classes * c) for i, c in enumerate(counts)}


def build_model(num_classes):
    base_model = MobileNetV2(
        weights="imagenet",
        include_top=False,
        input_shape=(IMG_SIZE, IMG_SIZE, 3)
    )

    base_model.trainable = True
    for layer in base_model.layers[:-35]:
        layer.trainable = False

    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dropout(0.4)(x)
    x = Dense(256, activation="relu")(x)
    x = Dropout(0.3)(x)
    output = Dense(num_classes, activation="softmax")(x)

    model = Model(inputs=base_model.input, outputs=output)
    model.compile(
        optimizer=Adam(learning_rate=1e-4),
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )
    return model


def main():
    train_aug = ImageDataGenerator(
        rescale=1.0 / 255.0,
        validation_split=VAL_SPLIT,
        rotation_range=20,
        zoom_range=0.2,
        horizontal_flip=True,
        width_shift_range=0.1,
        height_shift_range=0.1,
        brightness_range=[0.75, 1.25]
    )
    eval_aug = ImageDataGenerator(rescale=1.0 / 255.0)

    train_data = train_aug.flow_from_directory(
        TRAIN_DIR,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        subset="training",
        seed=SEED
    )
    val_data = train_aug.flow_from_directory(
        TRAIN_DIR,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        subset="validation",
        seed=SEED
    )
    test_data = eval_aug.flow_from_directory(
        TEST_DIR,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        shuffle=False
    )

    print("Class mapping:", train_data.class_indices)
    class_weights = _class_weights_from_generator(train_data)
    print("Class weights:", class_weights)

    model = build_model(num_classes=train_data.num_classes)

    os.makedirs(os.path.dirname(BEST_MODEL_PATH), exist_ok=True)
    callbacks = [
        EarlyStopping(monitor="val_loss", patience=6, restore_best_weights=True),
        ReduceLROnPlateau(monitor="val_loss", factor=0.4, patience=3, min_lr=1e-6),
        ModelCheckpoint(BEST_MODEL_PATH, monitor="val_loss", save_best_only=True)
    ]

    model.fit(
        train_data,
        validation_data=val_data,
        epochs=EPOCHS,
        callbacks=callbacks,
        class_weight=class_weights
    )

    if os.path.exists(BEST_MODEL_PATH):
        model = tf.keras.models.load_model(BEST_MODEL_PATH)

    test_loss, test_acc = model.evaluate(test_data, verbose=1)
    print(f"Test loss: {test_loss:.4f}")
    print(f"Test accuracy: {test_acc:.4f}")

    model.save(FINAL_MODEL_PATH)
    print(f"Saved final model to {FINAL_MODEL_PATH}")


if __name__ == "__main__":
    main()
