# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import gzip
import pickle
import numpy as np
from PIL import Image
from PIL import ImageStat
from trainer import boxscan


def genBackgrounds(filename):
    with gzip.open(filename, mode='wb') as d:
        result = {"data":[], "labels": []}
        imcount = 0
        for file_n in range(1, 89):
            loadfilename = "sample_data/USGS_public_domain/tr" + str(file_n) + ".png"
            print(loadfilename)
            tile_size = 20
            step_size = 15  # 1/4 image overlap
            zoom_step = 1.5
            skip = 13
            with Image.open(loadfilename) as im:
                i = 0
                for angle in range(0, 360, 45):
                    print("rotation angle: " + str(angle))
                    rot_im = im.rotate(angle, expand=True, resample=Image.BILINEAR)
                    for box in boxscan.genBox(rot_im.width, rot_im.height, tile_size, step_size, zoom_step, skip):
                        im2 = rot_im.crop(box)
                        # outfilename = "sample_data/USGS_public_domain/processed/tr{}_{:05d}.png".format(file_n, i)
                        im2 = im2.resize([tile_size, tile_size], resample=Image.BICUBIC)
                        pixmean = sum(ImageStat.Stat(im2).mean)
                        if pixmean > 300: # to eliminate black images with no info in the (rotation background)
                            data = np.asarray([im2.getdata(band=0), im2.getdata(band=1), im2.getdata(band=2)], dtype=np.uint8)
                            data = np.reshape(data, [-1])  # to get it in exactly the same format as planesnet data
                            result["data"].append(data)
                            result["labels"].append(0)  # not an airplane
                            # im2.save(outfilename)
                            i += 1
                            imcount +=1
        result["data"] = np.asarray(result["data"])  # to get it in exactly the same format as planesnet data
        pickle.dump(result, d)
        print("Saved {} background images to file {}".format(imcount, filename))

if __name__ == '__main__':
    genBackgrounds("sample_data/backgrounds.pklz")