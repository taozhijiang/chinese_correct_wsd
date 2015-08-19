FILENAME=news_tensite_xml_utf8.dat


sed -i '/<doc>/d' $FILENAME
sed -i '/<\/doc>/d' $FILENAME
sed -i '/<url>/d' $FILENAME
sed -i '/<docno>/d' $FILENAME
sed -i 's/<content>//g' $FILENAME
sed -i 's/<contenttitle>//g' $FILENAME
sed -i 's/<\/contenttitle>//g' $FILENAME
sed -i 's/<\/content>//g' $FILENAME

