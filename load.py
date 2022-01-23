import typing as t

import logging
import concurrent.futures

from loader import dataloader


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


loader_mapping = {
    "data/campaigns.csv": dataloader.CampaignLoader,
    "data/search_terms.csv": dataloader.SearchTerm,
    "data/adgroups.csv": dataloader.AdGroupLoader,
}


def load_data(
    *,
    data_source: str,
    data_loader: t.Type[dataloader.DataLoader],
) -> None:
    logging.info("Loading %s with %s", data_source, data_loader)
    data_loader(data_source).load()


def main() -> None:
    dataloader.init_loader()

    with concurrent.futures.ProcessPoolExecutor(
        max_workers=len(loader_mapping),
    ) as executor:
        futures = {
            executor.submit(
                load_data,
                data_source=data_source,
                data_loader=data_loader,
            )
            for data_source, data_loader in loader_mapping.items()
        }

        for future in concurrent.futures.as_completed(futures):
            yield future.result()


if __name__ == "__main__":
    [r for r in main()]

    retry_size = dataloader.RETRY_QUEUE.qsize()
    if retry_size:
        logging.error("%s items needs retrying", retry_size)
    else:
        logging.info("Done")
