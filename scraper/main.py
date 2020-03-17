from urllib import request
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import pandas as pd
from os import path


class MidKarScraper():
    ROOT_DOWNLOAD = "./midi"
    JAZZ_ROOT_URL = "http://midkar.com/jazz/jazz_{:0=2}.html"

    def get_midis(self) -> pd.DataFrame:
        print("start getting midis")

        dfs = []

        i = 1
        while True:
            df_page = self.download_music(i)

            if df_page is None:
                break

            dfs.append(df_page)
            i += 1

        return pd.concat(dfs)

    def download_music(self, page_number) -> pd.DataFrame or None:
        columns = ["title", "size", "performed_by", "sequencer", "file_name"]
        df = pd.DataFrame(columns=columns)

        try:
            html = request.urlopen(self.JAZZ_ROOT_URL.format(page_number))
        except HTTPError:
            return None

        soup = BeautifulSoup(html, "html.parser")

        table = soup.find_all("table")[1]
        trs = table.find_all("tr")

        for tr in trs[1:]:
            s = pd.Series(index=df.columns)
            tds = tr.find_all("td")
            print(tds[0].get_text())
            for i, td in enumerate(tds):
                s[columns[i]] = td.get_text()
                if i == 0:
                    a = td.find("a")
                    file_name = a["href"]

                    try:
                        request.urlretrieve(path.join(path.dirname(self.JAZZ_ROOT_URL), file_name),
                                            path.join(self.ROOT_DOWNLOAD, file_name))
                        s["file_name"] = file_name
                    except HTTPError:
                        pass

            df = df.append(s, ignore_index=True)

        return df


if __name__ == "__main__":
    mid_kar_scraper = MidKarScraper()
    df_musics = mid_kar_scraper.get_midis()
    df_musics.to_csv("musics.csv", index=False)
