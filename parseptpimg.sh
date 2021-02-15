#!/bin/bash


size=""
THUMBS=0

while [ "$#" -gt 0 ]; do
        key=${1}

        case ${key} in
                -t|--thumbs)
                        echo "Setting all parameter..."
                        THUMBS=1
                        shift
                        ;;
                -h|--help)
                        echo " "
			echo "ParsePimGupMe v1.3.3 (octaLSD)"
			echo " "
			echo "Usage: $0 [options]"
			echo " "
			echo "options: 			-t|--thumbs , create thumbnails with default 320 max scale"
			echo "				-s|--size SIZE, this is an option like '--xlarge' or '--large' or '--max-scale 960', enclosed in quotes" 
			echo " 				-h|--help, print this screen"
			echo " "
			exit
                        shift
                        ;;
                -s|--size)
                        echo "Setting older than date..."
                        size=${2}
                        shift
                        shift
                        ;;
                *)
                        shift
                        ;;
        esac
done



if [[ "$THUMBS" -eq "0" ]]; then
	echo "Not creating thumbnails..."
	sleep 2
	find ./ -maxdepth 1 -type f \( -iname \*.jpg -o -iname \*.png -o -iname \*.jpeg \) -print0 | xargs --null  pimgupme.py --bbcode -k 29db29a9-3822-4b58-bb3b-5416ab8f3ebe
	echo "Done."

else
	echo "Doing stuff..."
	find ./ -maxdepth 1 -type f \( -iname \*.jpg -o -iname \*.png -o -iname \*.jpeg \) -print0 | xargs --null  pimgupme.py --bbcode --thumbnails $size -k 29db29a9-3822-4b58-bb3b-5416ab8f3ebe
	echo "Done."
fi
