#!/usr/bin/python

#  # /usr/bin/env python

import codecs
import csv
import getopt
import sys
import time

SCRIPT_VERSION = 'v.1'
ENCODING = 'utf-8'

BANKS = []


def generate_res_bank(banksfile, outfile):
    head = '"abi","cab","id","name","street","zip","country:id"'
    out = codecs.open(outfile, 'w', encoding=ENCODING)
    out.write(u'{}\n'.format(head))
    tot = sum(1 for line in open(banksfile)) - 1
    startime = time.time()
    count = 0

    with open(banksfile, 'rb') as csvfile:
        f = csv.DictReader(csvfile, delimiter=';', quotechar='"')
        for b in f:
            stato = b['DES_STATO']
            if stato != 'ITALIA':
                continue

            abi = b['COD_MECC'].zfill(5)
            cab = b['CAB_SEDE'].zfill(5)

            if len(abi) < 4 or len(cab) < 4:
                # Too short, not a real CAB
                continue

            # Avoid duplicates and errors
            abicab = '{}{}'.format(abi, cab)
            if abicab in BANKS or '0000' in abi:
                continue

            # Store abi-cab => already done
            BANKS.append(abicab)

            abiname = b['DEN_160']
            bankname = abiname
            CAP = b['CAP']
            street = b['INDIRIZZO']
            outline = '"{}","{}","base.{}{}","{}","{}","{}","base.it"'.format(abi, cab, abi, cab, bankname, street, CAP)
            try:
                # CODEC CURRENTLY IS Western 1252 => cp1252
                out.write(u'{}\n'.format(outline.decode('cp1252')))
            except UnicodeDecodeError as e:
                print('** ERROR *** ' + e)

            count += 1
            if count % 5000 == 0:
                currtime = round(time.time() - startime, 2)
                summary = '{}/{}  {} s. ({} min.)'.format(count, tot, currtime, round(currtime / 60, 2))
                print(summary)

        currtime = round(time.time() - startime, 2)
    summary = '=== {}/{}  {} s. ({} min.)\n'.format(count, tot, currtime, round(currtime / 60, 2))
    print(summary)


def usage():
    print '''\nUsage: {name} [-h] -c= -a=
    --help:          show this message
    -b:              File con succursali banche
    
You may want to run this:

{name} -b SUCCURSALI_BANCHE.csv
    '''.format(name=sys.argv[0])


if __name__ == "__main__":

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hb:')
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    if len(opts) == 0:
        usage()
        sys.exit(2)

    dbname = ''

    action = ''
    banksfile = ''
    outfile = 'res.bank.csv'
    is_simulation = False
    force = False

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit(2)
        elif opt == '-b':
            banksfile = arg
        else:
            print('sconosciuta combinazione {}-{}', opt, arg)
            usage()
            sys.exit(2)

    if not banksfile:
        usage()
    else:
        answer = raw_input('\nATTENZIONE, viene generato (eventualmente sovrascritto) il file {}, continuare? (y/n) '.format(outfile))
        if answer not in ('y', 'yes'):
            print('\nCancellato dall\'utente\n')
            exit(1)

        generate_res_bank(banksfile, outfile)
        print('File generato.\n')

